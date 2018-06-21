import glob
import os
from pytest_girder.assertions import assertStatusOk


def uploadSampleData(server, admin, globPattern):
    testFiles = [i for i in glob.glob(globPattern) if not i.endswith('.json')]
    public = getPublicFolder(server, admin)
    items = []
    for testFile in testFiles:
        name = os.path.basename(testFile)
        with open(testFile, 'rb') as f:
            item = server.uploadFile(name, f.read(), admin, public)
            items.append(item)

    return items


def getPublicFolder(server, admin):
    public = server.request(path='/folder', user=admin,
                            params={'parentId': admin['_id'],
                                    'parentType': 'user',
                                    'name': 'Public'})
    assertStatusOk(public)
    return public.json[0]
