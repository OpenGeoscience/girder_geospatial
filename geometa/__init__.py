from girder import events
from girder.models.file import File
from girder.models.item import Item
from girder.plugin import GirderPlugin
from .rest import (geometa_search_handler, geometa_create_handler,
                   geometa_get_handler, create_geometa)


def file_upload_handler(event):
    _id = event.info['file']['_id']
    girder_file = File().load(_id, force=True)
    girder_item = Item().load(event.info['file']['itemId'], force=True)
    create_geometa(girder_item, girder_file)


class GeometaPlugin(GirderPlugin):
    DISPLAY_NAME = 'Geometa Plugin'

    def load(self, info):
        events.bind('model.file.finalizeUpload.after',
                    'name', file_upload_handler)
        info['apiRoot'].item.route('GET', ('geometa',),
                                   geometa_search_handler)
        info['apiRoot'].item.route('GET', (':id', 'geometa'),
                                   geometa_get_handler)
        info['apiRoot'].item.route('PUT', (':id', 'geometa'),
                                   geometa_create_handler)
