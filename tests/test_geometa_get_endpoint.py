import os
import glob
import pytest
from pytest_girder.assertions import assertStatusOk


def upload_sample_data(server, admin, public):
    testPath = 'tests/data/*.tif'
    testFile = glob.glob(testPath)[0]
    name = os.path.basename(testFile)
    with open(testFile, 'rb') as f:
        item = server.uploadFile(name, f.read(), admin, public.json[0])

    return item


@pytest.mark.plugin('geometa')
def test_geometa_get_endpoint(server, admin, fsAssetstore):
    public = server.request(path='/folder', user=admin,
                            params={'parentId': admin['_id'],
                                    'parentType': 'user',
                                    'name': 'Public'})
    assertStatusOk(public)
    uploaded = upload_sample_data(server, admin, public)

    resp = server.request(path='/item/{}/geometa'.format(uploaded['itemId']),
                          method='GET',
                          user=admin)

    assertStatusOk(resp)
    rasterKeys = sorted(['affine', 'bandInfo', 'bands', 'bounds',
                         'crs', 'driver', 'height', 'nativeBounds',
                         'type_', 'width'])

    assert sorted(resp.json.keys()) == rasterKeys
