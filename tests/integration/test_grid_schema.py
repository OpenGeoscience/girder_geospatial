import json
import pytest
from girder.models.item import Item
from geometa.constants import GEOMETA_FIELD
from ..utils import uploadSampleData


@pytest.mark.plugin('geometa')
@pytest.mark.parametrize('testFile, expected', [
    ('tests/data/sresa1b_ncar_ccsm3-example.nc',
     'tests/data/sresa1b_ncar_ccsm3-example_nc.json')
])
def test_grid_geometa(server, admin, fsAssetstore, testFile, expected):
    uploaded = uploadSampleData(server, admin, testFile)[0]
    document = Item().load(uploaded['itemId'], user=admin)
    with open(expected, 'r') as f:
        expectedJson = json.load(f)

    assert list(document[GEOMETA_FIELD]).sort() == list(expectedJson).sort()


@pytest.mark.plugin('geometa')
def test_union_subdataset_bounds(server, admin, fsAssetstore):
    testFile = 'tests/data/sresa1b_ncar_ccsm3-example.nc'
    uploaded = uploadSampleData(server, admin, testFile)[0]
    document = Item().load(uploaded['itemId'], user=admin)

    if document[GEOMETA_FIELD]['subDatasets'] == 1:
        expected = document[GEOMETA_FIELD]['subDatasetInfo'][0]['bounds']
        assert document[GEOMETA_FIELD]['bounds'] == expected
