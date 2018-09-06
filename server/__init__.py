from girder import events
from girder.models.item import Item
from .rest import (geometa_search_handler, geometa_create_handler,
                   geometa_get_handler, create_geometa)


def handler(event):
    girder_item = Item().load(event.info['itemId'], force=True)
    girder_file = list(Item().childFiles(girder_item, limit=1, force=True))[0]
    create_geometa(girder_item, girder_file)


def load(info):
    events.bind('model.file.save.after',
                info['name'], handler)
    info['apiRoot'].item.route('GET', ('geometa',),
                               geometa_search_handler)
    info['apiRoot'].item.route('GET', (':id', 'geometa'),
                               geometa_get_handler)
    info['apiRoot'].item.route('PUT', (':id', 'geometa'),
                               geometa_create_handler)
