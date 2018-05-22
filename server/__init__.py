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
    _id = event.info['file']['_id']
    girder_file = File().load(_id, force=True)
    path = _get_girder_path(girder_file)
    for entry_point_name, entry_point in Registry.items():
        try:
            metadata = entry_point(path)
            schema = BaseSchema()
            schema.load(metadata)
            # namespace metadata with entry point names
            # to avoid conflicts between handlers
            girder_file['geometa'] = {}
            girder_file['geometa'][entry_point_name] = metadata
            File().save(girder_file)
        except CannotHandleError:
            pass


def load(info):
    for entry_point in pkg_resources.iter_entry_points('geometa.formats'):
        Registry[entry_point.name] = entry_point.load()
    events.bind('model.file.finalizeUpload.after', info['name'], upload_handler)
