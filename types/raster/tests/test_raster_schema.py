import json
import os
import pytest
from pytest_girder.assertions import assertStatusOk
from girder.models.file import File


@pytest.mark.plugin('geometa')
@pytest.mark.parametrize('testFile, expected', [
    ('tests/data/byte.tif', 'tests/data/byte_tif.json'),
    ('tests/data/float.img', 'tests/data/float_img.json'),
    ('tests/data/byte.jp2', 'tests/data/byte_jp2.json'),
    ('tests/data/rgb.ntf', 'tests/data/rgb_ntf.json')
])
def test_raster_geometa(server, admin, fsAssetstore, testFile, expected):
    name = os.path.basename(testFile)
    public = server.request(path='/folder', user=admin, method='GET',
                            params={'parentId': admin['_id'],
                                    'parentType': 'user',
                                    'name': 'Public'})
    assertStatusOk(public)

    with open(testFile, 'rb') as f:
        uploadedFile = server.uploadFile(name, f.read(), admin, public.json[0])
        document = File().load(uploadedFile['_id'], user=admin)

    with open(expected) as f:
        expectedJson = json.load(f)

    assert document['geometa'] == expectedJson
