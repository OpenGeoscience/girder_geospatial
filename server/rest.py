from girder.api import access
from girder.api.rest import boundHandler
from girder.exceptions import ValidationException
from girder.models.item import Item
from girder.constants import AccessType
from geometa.schema import OpenSearchGeoSchema
from geometa import GEOSPATIAL_FIELD
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


@access.public
@boundHandler
def geometa_handler(self, params):
    schema = OpenSearchGeoSchema()
    user = self.getCurrentUser()
    try:
        params = schema.load(params)
    except ValidationError as e:
        raise ValidationException(e.messages)
    user = self.getCurrentUser()

    if 'geometry' in params:
        return get_documents_by_geometry(user, params['geometry'], params['relation'])
    elif 'bbox' in params:
        return get_documents_by_geometry(user, params['bbox'], params['relation'])
    elif 'latitude' in params:
        return get_documents_by_radius(user, params['latitude'],
                                       params['longitude'], params['radius'])
    else:
        return {}
