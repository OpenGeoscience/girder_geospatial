from girder import events
from girder.models.item import Item
from girder.plugin import GirderPlugin
from .constants import GEOMETA_CREATION_EVENT
from .rest import (geometa_search_handler, geometa_create_handler,
                   geometa_get_handler, create_geometa)


def file_upload_handler(event):
    file = event.info
    item_id = file.get('itemId')
    if item_id is None:
        return

    item = Item().load(item_id, force=True)
    if item and item.get('geometa') is None:
        if create_geometa(item, file):
            events.trigger(GEOMETA_CREATION_EVENT, info=event.info)


class GeometaPlugin(GirderPlugin):
    DISPLAY_NAME = 'Geometa Plugin'

    def load(self, info):
        events.bind('model.file.save.after',
                    'file_upload_handler', file_upload_handler)

        info['apiRoot'].item.route('GET', ('geometa',),
                                   geometa_search_handler)
        info['apiRoot'].item.route('GET', (':id', 'geometa'),
                                   geometa_get_handler)
        info['apiRoot'].item.route('PUT', (':id', 'geometa'),
                                   geometa_create_handler)
