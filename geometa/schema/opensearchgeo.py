import ast
import json
import geojson
from shapely.wkt import loads as load_wkt
from shapely.geos import WKTReadingError
from shapely.geometry import mapping, Polygon
from marshmallow.validate import Range, OneOf
from marshmallow import fields, Schema, validates_schema, ValidationError


class Relation(fields.Str):
    def _deserialize(self, value, att, obj):
        relationMapping = {
            'intersects': '$geoIntersects',
            'within': '$geoWithin'}
        return relationMapping[value]


class Geometry(fields.Str):
    def _deserialize(self, value, att, obj):
        try:
            geometry = load_wkt(value)
            return mapping(geometry)
        except WKTReadingError as e:
            try:
                raise ValidationError(e.message)
            # python3 hack for error message handling
            except AttributeError:
                raise ValidationError(str(e))


class Geojson(fields.Str):
    def _deserialize(self, value, att, obj):
        try:
            geojson_object = geojson.loads(json.dumps(ast.literal_eval(value)))
            try:
                geojson_object.is_valid
                return geojson_object
            except AttributeError:
                raise ValidationError('Invalid geojson is given')
        except ValueError:
            raise ValidationError('Invalid geojson is given')


class Bbox(fields.Str):
    def _deserialize(self, value, att, obj):
        bbox = [float(i) for i in value.split(',')]
        if len(bbox) != 4:
            message = 'BBox should be in "Xmin, Ymin, Xmax, Ymax" format'
            raise ValidationError(message)
        elif bbox[2] <= bbox[0]:
            message = 'Xmax must be greater than Xmin'
            raise ValidationError(message)
        elif bbox[3] <= bbox[1]:
            message = 'Ymax must be greater than Ymin'
            raise ValidationError(message)
        geometry = Polygon.from_bounds(*bbox)
        return mapping(geometry)


class OpenSearchGeoSchema(Schema):
    latitude = fields.Number(
        validate=Range(
            min=-90,
            max=90,
            error='Latitude must be between -90, 90'),
        metadata={
            'requires': ['longitude', 'radius'],
            'excludes': ['bbox', 'geometry', 'relation', 'geojson']
        }
    )
    longitude = fields.Number(
        validate=Range(
            min=-180,
            max=180,
            error='Longitude must be between -180, 180'),
        metadata={
            'requires': ['latitude', 'radius'],
            'excludes': ['bbox', 'geometry', 'relation', 'geojson']
        }
    )
    radius = fields.Number(
        validate=Range(
            min=0,
            error='Radius must be a positive number'),
        metadata={
            'requires': ['latitude', 'longitude'],
            'excludes': ['bbox', 'geometry', 'relation', 'geojson']
        }
    )
    relation = Relation(validate=OneOf(
        ['$geoIntersects', '$geoWithin'],
        error='Relation must be one of {choices}')
    )
    bbox = Bbox(
        metadata={
            'requires': ['relation'],
            'excludes': ['latitude', 'longitude', 'radius',
                         'geometry', 'geojson']
        }
    )
    geometry = Geometry(
        metadata={
            'requires': ['relation'],
            'excludes': ['latitude', 'longitude', 'radius', 'bbox', 'geojson']
        }
    )
    geojson = Geojson(
        metadata={
            'requires': ['relation'],
            'excludes': ['latitude', 'longitude', 'radius', 'bbox', 'geometry']
        }
    )
    start = fields.DateTime(
        metadata={
            'requires': ['end']
        }
    )
    end = fields.DateTime(
        metadata={
            'requires': ['start']
        }
    )

    def _key_should_exist_with_keys(self, context, key, keys):
        for i in keys:
            if i not in context:
                message = '{} should be provided with {}.'.format(key, keys)
                raise ValidationError(message)

    def _key_should_not_exist_with_keys(self, context, key, keys):
        for i in keys:
            if i in context:
                message = '{} and {} are mutually exclusive.'.format(key, keys)
                raise ValidationError(message)

    @validates_schema
    def validate_search_parameters(self, data):
        for key in data.keys():
            try:
                metadata = self.fields[key].metadata['metadata']
                self._key_should_exist_with_keys(data, key,
                                                 metadata['requires'])
                self._key_should_not_exist_with_keys(data, key,
                                                     metadata['excludes'])
            except KeyError:
                pass
