import pkg_resources
from girder.api import access
from girder.api.describe import autoDescribeRoute, Description
from girder.api.rest import boundHandler, filtermodel
from girder.models.item import Item
from girder.models.assetstore import Assetstore
from girder.constants import AccessType
from girder.utility import assetstore_utilities
from girder.utility._cache import cache
from geometa.schema import OpenSearchGeoSchema, BaseSchema
from geometa import GEOSPATIAL_FIELD, CannotHandleError


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


def get_geometa(girder_item, girder_file):
    path = _get_girder_path(girder_file)
    metadata = {}
    for entry_point_name, entry_point in get_type_handlers().items():
        try:
            metadata = entry_point(path)
        except CannotHandleError:
            pass

    return metadata


def create_geometa(girder_item, girder_file, geometa=None):
    metadata = get_geometa(girder_item, girder_file)
    if geometa:
        metadata = geometa

    if metadata:
        schema = BaseSchema()
        schema.load(metadata)
        girder_item['geometa'] = metadata
        Item().save(girder_item)
        Item().collection.create_index([(GEOSPATIAL_FIELD, "2dsphere")])

    return girder_item


@access.public
@boundHandler
@autoDescribeRoute(
    Description('Get geospatial metadata for a given item')
    .modelParam('id', 'The ID of the item that will have geospatial metadata.',
                model=Item, level=AccessType.READ)
)
def geometa_get_handler(self, item):
    girder_file = [i for i in Item().childFiles(item, limit=1)][0]
    return get_geometa(item, girder_file)


@access.public
@filtermodel(model=Item)
@boundHandler
@autoDescribeRoute(
    Description('Set geospatial metadata for a given item')
    .modelParam('id', 'The ID of the item that will have geospatial metadata.',
                model=Item, level=AccessType.READ)
    .jsonParam('geometa', 'Json object to save as geospatial metadata',
               required=False, default=None, requireObject=True)
)
def geometa_create_handler(self, item, geometa):
    girder_file = [i for i in Item().childFiles(item, limit=1)][0]
    return create_geometa(item, girder_file, geometa=geometa)


@access.public
@boundHandler
def geometa_search_handler(self, params):
    schema = OpenSearchGeoSchema()
    user = self.getCurrentUser()
    params = schema.load(params)
    user = self.getCurrentUser()
    documents = {}

    if 'geometry' in params:
        documents = get_documents_by_geometry(user,
                                              params['geometry'],
                                              params['relation'])
    elif 'bbox' in params:
        documents = get_documents_by_geometry(user,
                                              params['bbox'],
                                              params['relation'])
    elif 'latitude' in params:
        documents = get_documents_by_radius(user,
                                            params['latitude'],
                                            params['longitude'],
                                            params['radius'])
    elif 'geojson' in params:
        documents = get_documents_by_geometry(user,
                                              params['geojson'],
                                              params['relation'])

    return documents
