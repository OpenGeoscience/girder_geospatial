from shapely.wkt import loads as load_wkt
from shapely.geos import WKTReadingError
from shapely.geometry import mapping
from marshmallow.validate import Range, OneOf
from marshmallow import fields, Schema, validates_schema, ValidationError


class Relation(fields.Str):
    def _deserialize(self, value, att, obj):
        relationMapping = {
            'intersects': '$geoIntersects',
            'within': '$geoWithin',
            'near': '$near'}
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


class Bbox(fields.Str):
    def _deserialize(self, value, att, obj):
        bbox = [float(i) for i in value.split(',')]
        if len(bbox) != 4:
            raise ValidationError('BBox should be in "Xmin, Ymin, Xmax, Ymax" format')
        elif bbox[2] <= bbox[0]:
            raise ValidationError('Xmax must be greater than Xmin')
        elif bbox[3] <= bbox[1]:
            raise ValidationError('Ymax must be greater than Ymin')
        else:
            return bbox


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
    bbox = Bbox(
        metadata={
            'requires': [],
            'excludes': ['latitude', 'longitude', 'radius', 'geometry', 'relation']
        })
    geometry = Geometry(
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
