import os
import magic
import requests
from datetime import datetime

import model

dir_path = os.path.dirname(os.path.realpath(__file__))
images_folder = dir_path + '/images_stored/'


def save_image(session, url, name, username):
    response = requests.get(url, stream=True)
    if not response.ok:
        return {'ok': False, 'msg': 'Could not retrieve file.'}
    elif response.ok and 'image' not in response.headers['content-type']:
        return {'ok': False, 'msg': 'That\'s not an image !'}
    delete_image(session, name)
    session.add(model.Image(name=name, date=datetime.now(), sender=username, url=url))
    session.commit()
    return {'ok': True, 'msg': 'Image saved as "' + name + '".'}


def get_image(session, name):
    try:
        image = session.query(model.Image).filter(model.Image.name == name).filter(model.Image.active).order_by(-model.Image.date)[0]
        return {'ok': True, 'msg': image.url}
    except IndexError as e:
        return {'ok': False, 'msg': 'Unknown image name "' + name + '".'}


def get_list(session):
    head = "These images have been uploaded :\n"
    images = []
    for image in session.query(model.Image).filter(model.Image.active).order_by(model.Image.name):
        if image.name not in images:
            images.append(' - ' + image.name + ' - ' + str(image.active))
    return head + "\n".join(images)


def delete_image(session, name):
    try:
        image = session.query(model.Image).filter(model.Image.name == name).filter( model.Image.active).order_by(-model.Image.date)[0]
        image.active = False
        session.commit()
        return {'ok': True, 'msg': 'Successfully deleted image "' + name + '".'}
    except IndexError as e:
        return {'ok': False, 'msg': 'Unknown image name "' + name + '".'}
