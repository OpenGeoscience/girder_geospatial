import json
import pyproj
import geojson
from shapely.wkt import loads as load_wkt
from shapely.geos import WKTReadingError
from marshmallow import fields, Schema, validates, validates_schema, ValidationError
from marshmallow.validate import Range, OneOf


GEOSPATIAL_FIELD = 'geometa.bounds'


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


class Relation(fields.Str):
    def _deserialize(self, value, att, obj):
        relationMapping = {
            'intersects': '$geoIntersects',
            'within': '$geoWithin',
            'near': '$near'}
        return relationMapping[value]


class BaseSchema(Schema):
    crs = Crs(required=True)
    nativeBounds = fields.Dict(required=True)
    bounds = Bounds(required=True)
    type_ = fields.Str(required=True, validate=OneOf(
        ['raster', 'vector', 'pointcloud', 'grid'],
        error='type_ must be one of raster, vector, grid or pointcloud'))
    date = fields.DateTime(default='')
    altitudeEllipsoid = fields.String()
    nativeAltitude = fields.List(fields.Float)
    altitude = fields.List(fields.Float)


class OpenSearchGeoSchema(Schema):
    latitude = fields.Number(
        validate=Range(
            min=-90,
            max=90,
            error='Latitude must be between -90, 90'),
        metadata={
            'requires': ['longitude', 'radius'],
            'excludes': ['bbox', 'geometry', 'relation']
        })
    longitude = fields.Number(
        validate=Range(
            min=-180,
            max=180,
            error='Longitude must be between -180, 180'),
        metadata={
            'requires': ['latitude', 'radius'],
            'excludes': ['bbox', 'geometry', 'relation']
        })
    radius = fields.Number(
        validate=Range(
            min=0,
            error='Radius must be a positive number'),
        metadata={
            'requires': ['latitude', 'longitude'],
            'excludes': ['bbox', 'geometry', 'relation']
        })
    relation = Relation(validate=OneOf(
        ['$geoIntersects', '$geoWithin', '$near'],
        error='Relation must be one of {choices}'))
    bbox = fields.String(
        metadata={
            'requires': ['relation'],
            'excludes': ['latitude', 'longitude', 'radius', 'geometry']
        })
    geometry = fields.String(
        metadata={
            'requires': ['relation'],
            'excludes': ['latitude', 'longitude', 'radius', 'bbox']
        })
    start = fields.DateTime(
        metadata={
            'requires': ['end']
        })
    end = fields.DateTime(
        metadata={
            'requires': ['start']
        })

    @validates('bbox')
    def validate_bbox(self, value):
        bbox = [float(i) for i in value.split(',')]
        if len(bbox) != 4:
            raise ValidationError('BBox should be in "Xmin, Ymin, Xmax, Ymax" format')
        elif bbox[2] <= bbox[0]:
            raise ValidationError('Xmax must be greater than Xmin')
        elif bbox[3] <= bbox[1]:
            raise ValidationError('Ymax must be greater than Ymin')

    @validates('geometry')
    def validate_geometry(self, value):
        try:
            load_wkt(value)
        except WKTReadingError as e:
            try:
                raise ValidationError(e.message)
            # python3 hack for error message handling
            except AttributeError:
                raise ValidationError(str(e))

    def _key_should_exist_with_keys(self, context, key, keys):
        for i in keys:
            if i not in context:
                raise ValidationError('{} should be provided with {}.'.format(key, keys))

    def _key_should_not_exist_with_keys(self, context, key, keys):
        for i in keys:
            if i in context:
                raise ValidationError('{} and {} are mutually exclusive.'.format(key, keys))

    @validates_schema
    def validate_search_parameters(self, data):
        for key in data.keys():
            try:
                metadata = self.fields[key].metadata['metadata']
                self._key_should_exist_with_keys(data, key, metadata['requires'])
                self._key_should_not_exist_with_keys(data, key, metadata['excludes'])
            except KeyError:
                pass
