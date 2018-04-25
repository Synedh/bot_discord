import model

from flask import Flask, render_template

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine('sqlite:///account.db')
session = Session(engine)
model.Base.metadata.create_all(engine)

app = Flask(__name__)
app.debug = True
app.secret_key = 'qwertyuiop'


def get_images():
    return [image for image in session.query(model.Image).filter(model.Image.active)]


@app.route('/')
def index():
    return render_template('index.html', images=get_images())

if __name__ == "__main__":
    app.run()
