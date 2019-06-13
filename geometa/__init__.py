from girder import events
from girder.models.item import Item
from girder.plugin import GirderPlugin
from .rest import (geometa_search_handler, geometa_create_handler,
                   geometa_get_handler, create_geometa)


def file_upload_handler(event):
    file = event.info['file']
    if file.get('itemId'):
        girder_item = Item().load(file['itemId'], force=True)
        create_geometa(girder_item, file)
        events.trigger('geometa.created', info=event.info)


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
