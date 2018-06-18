import json
from geometa.schema import OpenSearchGeoSchema
from marshmallow import ValidationError
import pytest


@pytest.mark.parametrize("params", [
    {'latitude': 50},
    {'longitude': 50},
    {'radius': 50},
    {'radius': 50, 'latitude': 50, 'longitude': 50, 'relation': 'intersects'},
    {'bbox': '1,1,2,2'},
    {'bbox': '1,1,2', 'relation': 'intersects'},
    {'bbox': '1,1,1,2', 'relation': 'intersects'},
    {'bbox': '1,1,2,0', 'relation': 'intersects'},
    {'relation': 'intersects', 'geojson': 'foobar'},
    {'relation': 'intersects', 'geojson': json.dumps({
        "type": "Foobar",
        "coordinates": [
            -97.734375,
            40.17887331434696
        ]
    })},
    {'geometry': 'foobar'},
    {'geometry': 'POINT(6 10)'},
    {'geometry': 'POINT(6 10)', 'bbox': '1,1,2,2'},
    {'geometry': 'POINT(6 10)', 'radius': 40},
    {'start': '2018-06-23'}
])
def test_required_excluded_parameters(params):
    schema = OpenSearchGeoSchema()
    with pytest.raises(ValidationError):
        schema.load(params)
