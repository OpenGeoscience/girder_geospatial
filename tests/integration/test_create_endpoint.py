import json
import pytest
from girder.models.item import Item
from pytest_girder.assertions import assertStatusOk
from ..utils import uploadSampleData


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


@pytest.mark.plugin('geometa')
@pytest.mark.parametrize('geometa', [
    (
        {
            'crs': '',
            'type_': 'raster',
            'bounds': {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            -97.73400217294692,
                            40.17914177196121
                        ],
                        [
                            -97.73371249437332,
                            40.17914177196121
                        ],
                        [
                            -97.73371249437332,
                            40.17936924284886
                        ],
                        [
                            -97.73400217294692,
                            40.17936924284886
                        ],
                        [
                            -97.73400217294692,
                            40.17914177196121
                        ]
                    ]
                ]
            },
            'nativeBounds': {'left': 1,
                             'right': 1,
                             'top': 2,
                             'bottom': 2}
        }
    )
])
def test_geometa_create_with_user_data(server, admin, fsAssetstore, geometa):
    uploaded = uploadSampleData(server, admin, 'tests/data/*.tif')[0]

    server.request(path='/item/{}/geometa'.format(uploaded['itemId']),
                   params={'geometa': json.dumps(geometa)},
                   method='PUT',
                   user=admin)

    document = Item().load(uploaded['itemId'], user=admin)

    assert document['geometa'] == geometa


@pytest.mark.plugin('geometa')
@pytest.mark.parametrize('geometa', [
    ({'foo': 'bar'})
])
def test_bad_geometa_fails(server, admin, fsAssetstore, geometa):
    uploaded = uploadSampleData(server, admin, 'tests/data/*.tif')[0]

    resp = server.request(path='/item/{}/geometa'.format(uploaded['itemId']),
                          params={'geometa': json.dumps(geometa)},
                          method='PUT',
                          user=admin)

    assert resp.status == '400 Bad Request'


@pytest.mark.plugin('geometa')
@pytest.mark.parametrize('geometa', [
    (
        {
            'crs': '',
            'type_': 'raster',
            'bounds': {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            -97.73400217294692,
                            40.17914177196121
                        ],
                        [
                            -97.73371249437332,
                            40.17914177196121
                        ],
                        [
                            -97.73371249437332,
                            40.17936924284886
                        ],
                        [
                            -97.73400217294692,
                            40.17936924284886
                        ],
                        [
                            -97.73400217294692,
                            40.17914177196121
                        ]
                    ]
                ]
            },
            'nativeBounds': {'left': 1,
                             'right': 1,
                             'top': 2,
                             'bottom': 2},
            'foobar': 'barfoo'
        }
    )
])
def test_geometa_custom_data_is_returned(server, admin, fsAssetstore, geometa):
    uploaded = uploadSampleData(server, admin, 'tests/data/*.tif')[0]

    server.request(path='/item/{}/geometa'.format(uploaded['itemId']),
                   params={'geometa': json.dumps(geometa)},
                   method='PUT',
                   user=admin)

    response = server.request(
        path='/item/{}/geometa'.format(uploaded['itemId']),
        user=admin)

    assert 'foobar' in response.json.keys()
