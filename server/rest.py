from girder.api import access
from girder.api.rest import boundHandler
from girder.exceptions import ValidationException
from geometa.schema import OpenSearchGeoSchema
from marshmallow import ValidationError


@access.public
@boundHandler
def geometa_handler(self, params):
    schema = OpenSearchGeoSchema()
    try:
        params = schema.load(params)
    except ValidationError as e:
        raise ValidationException(e.messages)
    return params
