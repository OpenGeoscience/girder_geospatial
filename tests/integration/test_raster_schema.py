import json
import pytest
from girder.models.item import Item
from ..utils import uploadSampleData


@pytest.mark.plugin('geometa')
@pytest.mark.parametrize('testFile, expected', [
    ('tests/data/byte.tif', 'tests/data/byte_tif.json'),
    ('tests/data/float.img', 'tests/data/float_img.json'),
    ('tests/data/byte.jp2', 'tests/data/byte_jp2.json'),
    ('tests/data/rgb.ntf', 'tests/data/rgb_ntf.json')
])
def test_raster_geometa(server, admin, fsAssetstore, testFile, expected):
    uploaded = uploadSampleData(server, admin, testFile)[0]
    document = Item().load(uploaded['itemId'], user=admin)
    with open(expected) as f:
        expectedJson = json.load(f)

    assert list(document['geometa']).sort() == list(expectedJson).sort()
