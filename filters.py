from routes import app

@app.template_filter()
def favs(images):
	print('test')
	return images