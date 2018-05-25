from geometa.schema import BaseSchema
from geometa import from_bounds_to_geojson
import pytest
from marshmallow import ValidationError
import json


def sampleBounds():
    crs = '+proj=utm +zone=10 +datum=WGS84 +units=m +no_defs '
    nativeBounds = {'left': 271785.000,
                    'bottom': 4345785.000,
                    'right': 506715.000,
                    'top': 4584315.000}
    return from_bounds_to_geojson(nativeBounds, crs)


@pytest.mark.parametrize("crs, expected", [
    ('not a proj4 string', ''),
    ('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs ',
     '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs ')
])
def test_crs(crs, expected):
    metadata = {'bounds': sampleBounds(),
                'nativeBounds': {},
                'type_': 'raster'}
    metadata['crs'] = crs
    schema = BaseSchema()
    meta = schema.load(metadata)
    assert meta['crs'] == expected


@pytest.mark.parametrize('metadata', [
    ({'nativeBounds': '', 'type_': 'raster', 'bounds': sampleBounds()}),
    ({'crs': '', 'nativeBounds': '', 'bounds': sampleBounds()}),
    ({'crs': '', 'nativeBounds': '', 'type_': 'raster', 'bounds': sampleBounds()},
     {'crs': '', 'type_': 'raster', 'bounds': sampleBounds()})
])
def test_schema_with_missing_variables(metadata):
    schema = BaseSchema()
    with pytest.raises(ValidationError):
        schema.load(metadata)


@pytest.mark.parametrize('nativeBounds', [
    ('someBounds'),
    (['someBounds'])
])
def test_bad_native_bounds(nativeBounds):
    metadata = {'bounds': sampleBounds(),
                'type_': 'raster',
                'crs': ''}
    metadata['nativeBounds'] = nativeBounds
    schema = BaseSchema()
    with pytest.raises(ValidationError):
        schema.load(metadata)


@pytest.mark.parametrize('type_', [
    ('foobar')
])
def test_bad_type(type_):
    metadata = {'bounds': sampleBounds(),
                'nativeBounds': {},
                'crs': ''}
    metadata['type_'] = type_
    schema = BaseSchema()
    with pytest.raises(ValidationError):
        schema.load(metadata)


@pytest.mark.parametrize('bounds, message', [
    ('foobar', {'bounds': ['bounds must be a valid geojson geometry']}),
    (json.dumps(
        {"type": "LineString",
         "coordinates": [
             [
                 -100.94238281249999,
                 42.06560675405716
             ],
             [
                 -93.515625,
                 43.70759350405294
             ]
         ]}
    ), {'bounds': ['bounds must be a polygon']})
])
def test_bad_bounds(bounds, message):
    metadata = {'type_': 'raster',
                'crs': '',
                'nativeBounds': {}}
    metadata['bounds'] = bounds
    schema = BaseSchema()
    with pytest.raises(ValidationError) as exception:
        schema.load(metadata)
    assert exception.value.messages == message
