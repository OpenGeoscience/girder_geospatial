import json
import pytest
from girder.models.item import Item
from ..utils import uploadSampleData


@pytest.mark.plugin('geometa')
@pytest.mark.parametrize('testFile, expected', [
    ('tests/data/stations.geojson', 'tests/data/stations_geojson.json'),
    ('tests/data/geometries.kml', 'tests/data/geometries_kml.json')
])
def test_vector_geometa(server, admin, fsAssetstore, testFile, expected):
    uploaded = uploadSampleData(server, admin, testFile)[0]
    document = Item().load(uploaded['itemId'], user=admin)
    with open(expected) as f:
        expectedJson = json.load(f)

    assert list(document['geometa']).sort() == list(expectedJson).sort()


@pytest.mark.plugin('geometa')
def test_union_layer_bounds(server, admin, fsAssetstore):
    testFile = 'tests/data/stations.geojson'
    uploaded = uploadSampleData(server, admin, testFile)[0]
    document = Item().load(uploaded['itemId'], user=admin)

    if document['geometa']['layers'] == 1:
        expected = document['geometa']['layerInfo'][0]['bounds']
        assert document['geometa']['bounds'] == expected
