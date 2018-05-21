import pkg_resources
from girder import events
from girder.models.file import File
from girder.models.assetstore import Assetstore
from girder.utility import assetstore_utilities
from geometa.schema import BaseSchema
from geometa import CannotHandleError


Registry = {}


def _get_girder_path(girder_file):
    assetstore = Assetstore().load(girder_file['assetstoreId'])
    adapter = assetstore_utilities.getAssetstoreAdapter(assetstore)
    return adapter.fullPath(girder_file)


def upload_handler(event):
    for entry_point_name, entry_point in Registry.items():
        plugin = entry_point.load()
        _id = event.info['file']['_id']
        girder_file = File().load(_id, force=True)
        path = _get_girder_path(girder_file)
        try:
            metadata = plugin.handler(path)
            schema = BaseSchema()
            schema.load(metadata)
            if 'geometa' in girder_file:
                girder_file['geometa'][entry_point_name] = metadata
            else:
                girder_file['geometa'] = metadata
            File().save(girder_file)
        except CannotHandleError:
            pass


def load(info):
    for entry_point in pkg_resources.iter_entry_points('geometa.formats'):
        Registry[entry_point.name] = entry_point
    events.bind('model.file.finalizeUpload.after', info['name'], upload_handler)
