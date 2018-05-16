import pkg_resources
from girder import events
from girder.models.file import File
from girder.models.assetstore import Assetstore
from girder.utility import assetstore_utilities
from geometa.schema import BaseSchema


def _get_girder_path(girder_file):
    assetstore = Assetstore().load(girder_file['assetstoreId'])
    adapter = assetstore_utilities.getAssetstoreAdapter(assetstore)
    return adapter.fullPath(girder_file)


def upload_handler(event):
    for entry_point in pkg_resources.iter_entry_points('geometa.formats'):
        plugin = entry_point.load()
        _id = event.info['file']['_id']
        girder_file = File().load(_id, force=True)
        path = _get_girder_path(girder_file)
        try:
            metadata = plugin.handler(path)
            schema = BaseSchema()
            schema.load(metadata)
            girder_file['geometa'] = metadata
            File().save(girder_file)
        except AttributeError:
            pass


def load(info):
    events.bind('model.file.finalizeUpload.after', info['name'], upload_handler)
