import pytest
from ..utils import uploadSampleData


@pytest.mark.plugin('geometa')
def test_empty_params(server, admin):
    resp = server.request(path='/item/geometa', user=admin)
    assert resp.json == {}


@pytest.mark.plugin('geometa')
@pytest.mark.parametrize('params, expected', [
    (
        {'geometry': 'POLYGON ((-82.353515625 34.415973384481866, \
        -68.7744140625 34.415973384481866, -68.7744140625 41.244772343082076, \
        -82.353515625 41.244772343082076, -82.353515625 34.415973384481866))',
         'relation': 'intersects'},
        ['stations.geojson', 'sresa1b_ncar_ccsm3-example.nc']
    ),
    (
        {'bbox': '-82.353515625, 34.415973384481866, \
        -68.7744140625, 41.244772343082076',
         'relation': 'intersects'},
        ['stations.geojson', 'sresa1b_ncar_ccsm3-example.nc']
    ),
    (
        {'bbox': '-82.353515625, 34.415973384481866, \
        -68.7744140625, 41.244772343082076',
         'relation': 'within'},
        ['stations.geojson']
    ),
    (
        {
            "geojson": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            -101.77734374999999,
                            31.653381399664
                        ],
                        [
                            -27.59765625,
                            31.653381399664
                        ],
                        [
                            -27.59765625,
                            57.79794388498275
                        ],
                        [
                            -101.77734374999999,
                            57.79794388498275
                        ],
                        [
                            -101.77734374999999,
                            31.653381399664
                        ]
                    ]
                ]
            },
            "relation": "intersects"
        },
        ['stations.geojson', 'sresa1b_ncar_ccsm3-example.nc']
    )
])
def test_geospatial_query(server, admin, fsAssetstore, params, expected):
    uploadSampleData(server, admin, 'tests/data/*')
    resp = server.request(path='/item/geometa', user=admin, params=params)
    assert sorted([i['lowerName'] for i in resp.json]) == sorted(expected)


@pytest.mark.plugin('geometa')
@pytest.mark.parametrize('params', [
    ({'latitude': 'foobar'})
])
def test_bad_parameters_fail(server, admin, fsAssetstore, params):
    resp = server.request(path='/item/geometa', user=admin, params=params)
    assert resp.status == '400 Bad Request'
