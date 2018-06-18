import os
import glob
import pytest
from girder.models.item import Item
from pytest_girder.assertions import assertStatusOk


def upload_sample_data(server, admin, public):
    testPath = 'tests/data/*.tif'
    testFile = glob.glob(testPath)[0]
    name = os.path.basename(testFile)
    with open(testFile, 'rb') as f:
        item = server.uploadFile(name, f.read(), admin, public.json[0])

    return item


@pytest.mark.plugin('geometa')
def test_geometa_create_endpoint(server, admin, fsAssetstore):
    public = server.request(path='/folder', user=admin,
                            params={'parentId': admin['_id'],
                                    'parentType': 'user',
                                    'name': 'Public'})
    assertStatusOk(public)
    uploaded = upload_sample_data(server, admin, public)
    document = Item().load(uploaded['itemId'], user=admin)

    # Remove geometa from item and recreate it using the endpoint
    # as opposed to relying on upload event
    del document['geometa']
    Item().updateItem(document)
    resp = server.request(path='/item/{}/geometa'.format(uploaded['itemId']),
                          method='PUT',
                          user=admin)

    assertStatusOk(resp)

    document = Item().load(uploaded['itemId'], user=admin)
    assert 'geometa' in document
