import pkg_resources
from girder.api import access
from girder.api.describe import autoDescribeRoute, Description
from girder.api.rest import boundHandler, filtermodel
from girder.exceptions import ValidationException
from girder.models.item import Item
from girder.models.assetstore import Assetstore
from girder.constants import AccessType
from girder.utility import assetstore_utilities
from girder.utility._cache import cache
from geometa.schema import OpenSearchGeoSchema, BaseSchema
from geometa import GEOSPATIAL_FIELD, CannotHandleError
from marshmallow import ValidationError


def _find(user, query):
    cursor = Item().find(query)

    return list(Item().filterResultsByPermission(
        cursor, user, AccessType.READ))


def get_documents_by_geometry(user, geometry, relation):
    query = {
        GEOSPATIAL_FIELD: {
            relation: {
                '$geometry': geometry
            }
        }
    }

    return _find(user, query)


def get_documents_by_radius(user, latitude, longitude, radius):
    RADIUS_OF_EARTH = 6378137.0  # average in meters
    query = {
        GEOSPATIAL_FIELD: {
            '$geoWithin': {'$centerSphere': [
                [longitude, latitude],
                radius / RADIUS_OF_EARTH]}
        }
    }

    return _find(user, query)


def _get_girder_path(girder_file):
    assetstore = Assetstore().load(girder_file['assetstoreId'])
    adapter = assetstore_utilities.getAssetstoreAdapter(assetstore)
    return adapter.fullPath(girder_file)


@cache.cache_on_arguments()
def get_type_handlers():
    entry_points = pkg_resources.iter_entry_points('geometa.types')
    return {e.name: e.load() for e in entry_points}


def create_geometa(girder_item, girder_file):
    path = _get_girder_path(girder_file)
    for entry_point_name, entry_point in get_type_handlers().items():
        try:
            metadata = entry_point(path)
            schema = BaseSchema()
            schema.load(metadata)
            girder_item['geometa'] = metadata
            Item().save(girder_item)
            Item().collection.create_index([(GEOSPATIAL_FIELD, "2dsphere")])
        except CannotHandleError:
            pass
    return girder_item


@access.public
@filtermodel(model=Item)
@boundHandler
@autoDescribeRoute(
    Description('Create geospatial metadata for a given item')
    .modelParam('id', 'The ID of the item that will have geospatial metadata.',
                model=Item, level=AccessType.READ)
)
def geometa_create_handler(self, item):
    girder_file = [i for i in Item().childFiles(item, limit=1)][0]
    return create_geometa(item, girder_file)


@access.public
@boundHandler
def geometa_search_handler(self, params):
    schema = OpenSearchGeoSchema()
    user = self.getCurrentUser()
    try:
        params = schema.load(params)
    except ValidationError as e:
        raise ValidationException(e.messages)
    user = self.getCurrentUser()

    if 'geometry' in params:
        return get_documents_by_geometry(user,
                                         params['geometry'],
                                         params['relation'])
    elif 'bbox' in params:
        return get_documents_by_geometry(user,
                                         params['bbox'],
                                         params['relation'])
    elif 'latitude' in params:
        return get_documents_by_radius(user, params['latitude'],
                                       params['longitude'], params['radius'])
    elif 'geojson' in params:
        return get_documents_by_geometry(user,
                                         params['geojson'],
                                         params['relation'])

    else:
        return {}
