from girder import events


def handler(event):
    print event.info


def load(info):

    name = info['name']
    events.bind('model.file.finalizeUpload.after', name, handler)
