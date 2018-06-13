from girder.api import access
from girder.api.rest import boundHandler
from girder.exceptions import ValidationException
from girder.models.item import Item
from girder.constants import AccessType
from geometa.schema import OpenSearchGeoSchema
from geometa import GEOSPATIAL_FIELD
from marshmallow import ValidationError


def _find(user, query, limit, offset, sort):
    """
    Helper to search the geospatial data of items and return the filtered
    fields and geospatial data of the matching items.

    :param query: geospatial search query.
    :type query: dict[str, unknown]
    :param limit: maximum number of matching items to return.
    :type limit: int
    :param offset: offset of matching items to return.
    :type offset: int
    :param sort: field by which to sort the matching items
    :type sort: str
    :returns: filtered fields of the matching items with geospatial data
             appended to the 'geo' field of each item.
    :rtype : list[dict[str, unknown]]
    """
    cursor = Item().find(query, sort=sort)

    return list(Item().filterResultsByPermission(
        cursor, user, AccessType.READ, limit, offset))


def intersects(user, geometry, limit=1000, offset=0, sort=None):
    query = {
        GEOSPATIAL_FIELD: {
            '$geoIntersects': {
                '$geometry': geometry
            }
        }
    }

    return _find(user, query, limit, offset, sort)


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
        return intersects(user, params['geometry'])
    else:
        return {}
