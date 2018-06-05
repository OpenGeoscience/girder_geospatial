import json
from marshmallow import Schema, fields, ValidationError
import pyproj
import geojson


class Crs(fields.Field):
    def _deserialize(self, value, attr, obj):
        try:
            pyproj.Proj(value, errcheck=True)
            return value
        except RuntimeError:
            return ''


class Bounds(fields.Field):
    def _deserialize(self, value, attr, obj):
        try:
            geojson_obj = geojson.loads(json.dumps(value))
            if geojson_obj.is_valid and geojson_obj['type'] == 'Polygon':
                return value
            else:
                raise ValidationError('bounds must be a polygon')
        except AttributeError:
            raise ValidationError('bounds must be a valid geojson geometry')


class Type_(fields.Field):
    def _deserialize(self, value, att, obj):
        if value in ['raster', 'vector', 'pointcloud', 'grid']:
            return value
        else:
            message = 'type_ must be one of raster, vector, grid or pointcloud'
            raise ValidationError(message)


class BaseSchema(Schema):
    crs = Crs(required=True)
    nativeBounds = fields.Dict(required=True)
    bounds = Bounds(required=True)
    type_ = Type_(required=True)
    date = fields.Date(default='')
    altitudeEllipsoid = fields.String()
    nativeAltitude = fields.List(fields.Float)
    altitude = fields.List(fields.Float)
