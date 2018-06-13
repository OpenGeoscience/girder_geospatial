import os
import glob
import pytest
from pytest_girder.assertions import assertStatusOk


def upload_sample_data(server, admin, public):
    testPath = 'tests/data/*'
    testFiles = [i for i in glob.glob(testPath) if not i.endswith('.json')]

    for testFile in testFiles:
        name = os.path.basename(testFile)
        with open(testFile, 'rb') as f:
            server.uploadFile(name, f.read(), admin, public.json[0])


@pytest.mark.plugin('geometa')
def test_empty_params(server, admin):
    resp = server.request(path='/item/geometa', user=admin)
    assert resp.json == {}


@pytest.mark.plugin('geometa')
@pytest.mark.parametrize('params, expected', [
    (
        {'geometry': 'POLYGON ((-82.353515625 34.415973384481866, -68.7744140625 34.415973384481866, \
        -68.7744140625 41.244772343082076, -82.353515625 41.244772343082076, -82.353515625 34.415973384481866))',
         'relation': 'intersects'},
        ['stations.geojson', 'sresa1b_ncar_ccsm3-example.nc']
    ),
    (
        {'bbox': '-82.353515625, 34.415973384481866, -68.7744140625, 41.244772343082076',
         'relation': 'intersects'},
        ['stations.geojson', 'sresa1b_ncar_ccsm3-example.nc']
    ),
    (
        {'bbox': '-82.353515625, 34.415973384481866, -68.7744140625, 41.244772343082076',
         'relation': 'within'},
        ['stations.geojson']
    ),
    (
        {'longitude': -82.353515625, 'latitude': 34.415973384481866, 'radius': 1000000},
        ['stations.geojson']
    )
])
def test_geospatial_query(server, admin, fsAssetstore, params, expected):
    public = server.request(path='/folder', user=admin,
                            params={'parentId': admin['_id'],
                                    'parentType': 'user',
                                    'name': 'Public'})
    assertStatusOk(public)
    upload_sample_data(server, admin, public)
    resp = server.request(path='/item/geometa', user=admin, params=params)
    assert sorted([i['lowerName'] for i in resp.json]) == sorted(expected)
