import json
import os
import pytest
from pytest_girder.assertions import assertStatusOk
from girder.models.item import Item


@pytest.mark.plugin('geometa')
@pytest.mark.parametrize('testFile, expected', [
    ('tests/data/sresa1b_ncar_ccsm3-example.nc',
     'tests/data/sresa1b_ncar_ccsm3-example_nc.json')
])
def test_grid_geometa(server, admin, fsAssetstore, testFile, expected):
    name = os.path.basename(testFile)
    public = server.request(path='/folder', user=admin, method='GET',
                            params={'parentId': admin['_id'],
                                    'parentType': 'user',
                                    'name': 'Public'})
    assertStatusOk(public)

    with open(testFile, 'rb') as f:
        uploadedFile = server.uploadFile(name, f.read(), admin, public.json[0])
        document = Item().load(uploadedFile['itemId'], user=admin)

    with open(expected, 'r') as f:
        expectedJson = json.load(f)

    assert list(document['geometa']).sort() == list(expectedJson).sort()


@pytest.mark.plugin('geometa')
def test_union_subdataset_bounds(server, admin, fsAssetstore):
    testFile = 'tests/data/sresa1b_ncar_ccsm3-example.nc'
    name = os.path.basename(testFile)

    public = server.request(path='/folder', user=admin, method='GET',
                            params={'parentId': admin['_id'],
                                    'parentType': 'user',
                                    'name': 'Public'})
    assertStatusOk(public)

    with open(testFile, 'rb') as f:
        uploadedFile = server.uploadFile(name, f.read(), admin, public.json[0])
        document = Item().load(uploadedFile['itemId'], user=admin)

    if document['geometa']['subDatasets'] == 1:
        expected = document['geometa']['subDatasetInfo'][0]['bounds']
        assert document['geometa']['bounds'] == expected
