import json
import os
import pytest
from pytest_girder.assertions import assertStatusOk
from girder.models.item import Item


@pytest.mark.plugin('geometa')
@pytest.mark.parametrize('testFile, expected', [
    ('tests/data/stations.geojson', 'tests/data/stations_geojson.json'),
    ('tests/data/geometries.kml', 'tests/data/geometries_kml.json')
])
def test_vector_geometa(server, admin, fsAssetstore, testFile, expected):
    name = os.path.basename(testFile)
    public = server.request(path='/folder', user=admin, method='GET',
                            params={'parentId': admin['_id'],
                                    'parentType': 'user',
                                    'name': 'Public'})
    assertStatusOk(public)

    with open(testFile, 'rb') as f:
        uploadedFile = server.uploadFile(name, f.read(), admin, public.json[0])
        document = Item().load(uploadedFile['itemId'], user=admin)

    with open(expected) as f:
        expectedJson = json.load(f)

    assert list(document['geometa']).sort() == list(expectedJson).sort()


@pytest.mark.plugin('geometa')
def test_union_layer_bounds(server, admin, fsAssetstore):
    testFile = 'tests/data/stations.geojson'
    name = os.path.basename(testFile)

    public = server.request(path='/folder', user=admin, method='GET',
                            params={'parentId': admin['_id'],
                                    'parentType': 'user',
                                    'name': 'Public'})
    assertStatusOk(public)

    with open(testFile, 'rb') as f:
        uploadedFile = server.uploadFile(name, f.read(), admin, public.json[0])
        document = Item().load(uploadedFile['itemId'], user=admin)

    if document['geometa']['layers'] == 1:
        expected = document['geometa']['layerInfo'][0]['bounds']
        assert document['geometa']['bounds'] == expected
