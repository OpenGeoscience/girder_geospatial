from geometa.schema import OpenSearchGeoSchema
from marshmallow import ValidationError
import pytest


@pytest.mark.parametrize("params", [
    {'latitude': 50},
    {'longitude': 50},
    {'radius': 50},
    {'radius': 50, 'latitude': 50, 'longitude': 50, 'relation': 'intersects'},
    {'bbox': '1,1,2,2'},
    {'relation': 'intersects', 'geojson': 'foobar'},
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
