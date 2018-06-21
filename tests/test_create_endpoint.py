import pytest
from girder.models.item import Item
from pytest_girder.assertions import assertStatusOk
from .utils import uploadSampleData


@pytest.mark.plugin('geometa')
def test_geometa_create_endpoint(server, admin, fsAssetstore):
    uploaded = uploadSampleData(server, admin, 'tests/data/*.tif')[0]
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
