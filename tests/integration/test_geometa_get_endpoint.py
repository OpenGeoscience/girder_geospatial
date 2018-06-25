import pytest
from pytest_girder.assertions import assertStatusOk
from ..utils import uploadSampleData


@pytest.mark.plugin('geometa')
def test_geometa_get_endpoint(server, admin, fsAssetstore):
    uploaded = uploadSampleData(server, admin, 'tests/data/*.tif')[0]

    resp = server.request(path='/item/{}/geometa'.format(uploaded['itemId']),
                          method='GET',
                          user=admin)

    assertStatusOk(resp)
    rasterKeys = sorted(['affine', 'bandInfo', 'bands', 'bounds',
                         'crs', 'driver', 'height', 'nativeBounds',
                         'type_', 'width'])

    assert sorted(resp.json.keys()) == rasterKeys
