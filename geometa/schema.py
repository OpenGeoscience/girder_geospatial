from marshmallow import Schema, fields
import pyproj


class Crs(fields.Field):
    def _deserialize(self, value, attr, obj):
        try:
            pyproj.Proj(value, errcheck=True)
            return value
        except RuntimeError:
            return ''


class Bounds(fields.Field):
    # TODO: Validate native bounds
    def _deserialize(self, value, attr, obj):
        return value


class BaseSchema(Schema):
    crs = Crs(required=True)
    nativeBounds = fields.Dict(required=True)
    bounds = Bounds(required=True)
    type_ = fields.String(required=True)
    date = fields.Date(default='')
    # TODO: Validate altitude fields
    altitudeEllipsoid = fields.String()
    nativeAltitude = fields.List(fields.Float)
    altitude = fields.List(fields.Float)
