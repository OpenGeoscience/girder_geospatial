import pkg_resources
import inspect
from girder.api import access
from girder.api.describe import autoDescribeRoute, describeRoute, Description
from girder.api.rest import boundHandler, filtermodel
from girder.exceptions import ValidationException
from girder.models.item import Item
from girder.models.assetstore import Assetstore
from girder.constants import AccessType
from girder.utility import assetstore_utilities
from girder.utility._cache import cache
from geometa.schema import OpenSearchGeoSchema, BaseSchema
from .constants import GEOSPATIAL_FIELD, GEOSPATIAL_SUBDATASETS_FIELD
from .exceptions import CannotHandleError
from marshmallow import ValidationError


def _find(user, query):
    cursor = Item().find(query)

    return list(Item().filterResultsByPermission(
        cursor, user, AccessType.READ))


def get_documents_by_geometry(user, geometry, relation):
    query = {
        '$or': [
            {
                GEOSPATIAL_FIELD: {
                    relation: {
                        '$geometry': geometry
                    }
                }
            },
            {
                GEOSPATIAL_SUBDATASETS_FIELD: {
                    relation: {
                        '$geometry': geometry
                    }
                }
            }
        ]

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
    return {e.name: [e.load(), inspect.getargspec(e.load()).args]
            for e in entry_points}


def get_geometa(girder_item, girder_file):
    path = _get_girder_path(girder_file)
    metadata = {}
    for entry_point_name, [handler, args] in get_type_handlers().items():
        kwargs = {}
        if 'girder_item' in args:
            kwargs['girder_item'] = girder_item
        if 'girder_file' in args:
            kwargs['girder_file'] = girder_file
        try:
            metadata = handler(path, **kwargs)
        except CannotHandleError:
            pass

    return metadata


def create_geometa(girder_item, girder_file, metadata=None):
    if not metadata:
        metadata = get_geometa(girder_item, girder_file)

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
    try:
        return item['geometa']
    except KeyError:
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
    girder_file = None
    if not geometa:
        girder_file = [i for i in Item().childFiles(item, limit=1)][0]
    try:
        return create_geometa(item, girder_file, geometa)
    except ValidationError as e:
        raise ValidationException(e.messages)


@access.public
@boundHandler
@describeRoute(
    Description('Query for the items that matches a given geospatial criteria')
    .param('latitude', 'Latitude of the search point', required=False)
    .param('longitude', 'Longitude of the search point', required=False)
    .param('radius', 'Radius of the search circle', required=False)
    .param('relation', 'Relation parameter for the query', required=False)
    .param('bbox', 'Bounding box parameter', required=False)
    .param('geometry', 'Geojson geometry for the query in wkt format',
           required=False)
    .param('geojson', 'Geojson geometry for the query', required=False)
)
def geometa_search_handler(self, params):
    schema = OpenSearchGeoSchema()
    user = self.getCurrentUser()
    try:
        params = schema.load(params)
    except ValidationError as e:
        raise ValidationException(e.messages)
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
