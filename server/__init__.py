from girder import events
from girder.models.file import File
from girder.models.item import Item
from .rest import geometa_search_handler, geometa_create_handler
from .rest import create_geometa


def file_upload_handler(event):
    _id = event.info['file']['_id']
    girder_file = File().load(_id, force=True)
    girder_item = Item().load(event.info['file']['itemId'], force=True)
    create_geometa(girder_item, girder_file)


def load(info):
    events.bind('model.file.finalizeUpload.after',
                info['name'], file_upload_handler)
    info['apiRoot'].item.route('GET', ('geometa',),
                               geometa_search_handler)
    info['apiRoot'].item.route('PUT', (':id', 'geometa'),
                               geometa_create_handler)
