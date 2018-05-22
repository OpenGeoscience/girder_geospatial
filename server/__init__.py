import pkg_resources
from girder import events
from girder.models.file import File
from girder.models.assetstore import Assetstore
from girder.utility import assetstore_utilities
from girder.utility._cache import cache
from geometa.schema import BaseSchema
from geometa import CannotHandleError


def _get_girder_path(girder_file):
    assetstore = Assetstore().load(girder_file['assetstoreId'])
    adapter = assetstore_utilities.getAssetstoreAdapter(assetstore)
    return adapter.fullPath(girder_file)


@cache.cache_on_arguments()
def get_handlers():
    entry_points = pkg_resources.iter_entry_points('geometa.formats')
    return {e.name: e.load() for e in entry_points}


def upload_handler(event):
    _id = event.info['file']['_id']
    girder_file = File().load(_id, force=True)
    path = _get_girder_path(girder_file)
    for entry_point_name, entry_point in get_handlers().items():
        try:
            metadata = entry_point(path)
            schema = BaseSchema()
            schema.load(metadata)
            girder_file['geometa'] = metadata
            File().save(girder_file)
        except CannotHandleError:
            pass


def load(info):
    events.bind('model.file.finalizeUpload.after', info['name'], upload_handler)
