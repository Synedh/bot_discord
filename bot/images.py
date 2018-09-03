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
    session.add(model.Image(name=name, date=datetime.now(), sender=username, url=url, used=0))
    session.commit()
    return {'ok': True, 'msg': 'Image saved as "' + name + '".'}


def get_image(session, name):
    try:
        image = session.query(model.Image).filter(model.Image.name == name).filter(model.Image.active).order_by(-model.Image.date)[0]
        image.used = image.used + 1
        session.commit()
        return {'ok': True, 'msg': image.url}
    except IndexError as e:
        return {'ok': False, 'msg': 'Unknown image name "' + name + '".'}


def get_list(session):
    head = "These images have been uploaded :\n"
    images = []
    for image in session.query(model.Image).filter(model.Image.active).order_by(model.Image.name):
        if image.name not in images:
            images.append(image.name)
    text = ['']
    i = 0
    while i < len(images):
        line = ''
        try:
            line += '{0:30}  {1:30} {2}\n'.format(images[i], images[i + 1], images[i + 2])
            i += 3
        except IndexError as e:
            try:
                line += '{0:30}  {1}\n'.format(images[i], images[i + 1])
                i += 2
            except IndexError as e:
                line += images[i] + '\n'
                i += 1
        if len(text[-1] + line) >= 2000:
            text.append(line)
        else:
            text[-1] += line
    return text


def delete_image(session, name):
    try:
        image = session.query(model.Image).filter(model.Image.name == name).filter( model.Image.active).order_by(-model.Image.date)[0]
        image.active = False
        session.commit()
        return {'ok': True, 'msg': 'Successfully deleted image "' + name + '".'}
    except IndexError as e:
        return {'ok': False, 'msg': 'Unknown image name "' + name + '".'}
