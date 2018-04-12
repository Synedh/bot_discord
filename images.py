import os
import magic
import requests
from datetime import datetime

dir_path = os.path.dirname(os.path.realpath(__file__))
images_folder = dir_path + '/images_stored/'

def save_image(url, name, username):
    response = requests.get(url, stream=True)
    if not response.ok:
        return {'ok': False, 'msg': 'Could not retrieve file.'}
    elif response.ok and 'image' not in response.headers['content-type']:
        return {'ok': False, 'msg': 'That\'s not an image !'}
    elif response.ok and int(response.headers['content-length']) >= 1000000:
        return {'ok': False, 'msg': 'Image too big, should be under 1Mo.'}    

    filename = datetime.now().strftime('%Y%m%d%H%M%S') + '_' + username + '_' + name + '.' + url.split('.')[-1]
    try:
        with open(images_folder + filename, 'wb') as file:
            file.write(response.content)
    except IOError as e:
        return {'ok': False, 'msg': str(e)}
    return {'ok': True, 'msg': 'Done.'}


def get_image(name):
    for image in reversed(os.listdir(images_folder)):
        if image.split('.')[0].split('_')[-1] == name:
            return {'ok': True, 'msg' : images_folder + image}
    return {'ok': False, 'msg': 'Unknown image name "' + name + '".'}
