import os

dir_path = os.path.dirname(os.path.realpath(__file__))
images_folder = 'images_stored'

def save_image(url, name):
	return True

def get_image(name):
	return dir_path + '/' + images_folder + '/' + '292.w200h.png'
