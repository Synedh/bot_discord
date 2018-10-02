import model
from bot import images

import os
from datetime import datetime
from requests_oauthlib import OAuth2Session
from flask import Flask, render_template, session, request, url_for, redirect, _request_ctx_stack, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

with open('token') as file:
    file.readline()
    OAUTH2_CLIENT_ID = file.readline()[:-1].split('=')[1]
    OAUTH2_CLIENT_SECRET = file.readline()[:-1].split('=')[1]
    OAUTH2_REDIRECT_URI = file.readline()[:-1].split('=')[1]

API_BASE_URL = 'https://discordapp.com/api'
AUTHORIZATION_BASE_URL = API_BASE_URL + '/oauth2/authorize'
TOKEN_URL = API_BASE_URL + '/oauth2/token'

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = OAUTH2_CLIENT_SECRET

if 'http://' in OAUTH2_REDIRECT_URI:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'


def token_updater(token):
    session['oauth2_token'] = token


def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=OAUTH2_CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=OAUTH2_REDIRECT_URI,
        auto_refresh_kwargs={
            'client_id': OAUTH2_CLIENT_ID,
            'client_secret': OAUTH2_CLIENT_SECRET,
        },
        auto_refresh_url=TOKEN_URL,
        token_updater=token_updater)


def is_tite_in_guilds(guilds):
    for guild in guilds:
        try:
            if guild['id'] == '202909295526805505':
                return guild
        except TypeError as e:
            pass
    return False


def has_permission(perm):
    return bool(perm & 0x10000000)


def get_current_user(s):
    discord_session = make_session(token=session.get('oauth2_token'))
    user = discord_session.get(API_BASE_URL + '/users/@me').json()
    guilds = discord_session.get(API_BASE_URL + '/users/@me/guilds').json()
    if 'code' in user or type(guilds) == dict:
        return None, None
    queryuser = s.query(model.User).filter(model.User.id == user['id'])
    if queryuser.count() == 0:
        current_user = model.User(
            id=user['id'], 
            username=user['username'] + '#' + user['discriminator'], 
            isInTite=bool(is_tite_in_guilds(guilds)), 
            hasEnougthRank=has_permission(is_tite_in_guilds(guilds)['permissions'])
        )
        s.add(current_user)
    else:
        current_user = queryuser.first()
        if current_user.username != (user['username'] + '#' + user['discriminator']):
            current_user.username = user['username'] + '#' + user['discriminator']
        if current_user.isInTite != bool(is_tite_in_guilds(guilds)):
            current_user.isInTite = bool(is_tite_in_guilds(guilds))
        if current_user.hasEnougthRank != has_permission(is_tite_in_guilds(guilds)['permissions']):
            current_user.hasEnougthRank = has_permission(is_tite_in_guilds(guilds)['permissions'])
    s.commit()
    return current_user, user['avatar']


@app.template_filter()
def fav_ordering(images, user):
    def isin(image, images):
        for img in images:
            if img.id == image.id:
                return True
        return False

    try:
        user_images = user.images
    except AttributeError as e:
        return images

    favs = []
    for image in images:
        if isin(image, user_images):
            favs.append(image)
    for image in images:
        if not isin(image, user_images):
            favs.append(image)
    return favs


@app.route('/')
def index():
    session = Session(create_engine('sqlite:///account.db'))
    current_user, avatar = get_current_user(session)
    images = [image for image in session.query(model.Image).filter(model.Image.active)]
    return render_template('index.html', images=images, user=current_user, avatar=avatar)


@app.route('/users')
def users():
    session = Session(create_engine('sqlite:///account.db'))
    current_user, avatar = get_current_user(session)
    users = []
    return render_template('users.html', users=users, user=current_user, avatar=avatar)



@app.route('/upload', methods=['POST'])
def upload_image():
    user_id = request.json['user_id']
    image_name = request.json['image_name']
    image_url = request.json['image_url']
    s = Session(create_engine('sqlite:///account.db'))
    user = s.query(model.User).filter(model.User.id == user_id).first()
    images.save_image(s, image_url, image_name, user.username)
    return jsonify({'user_id': user.id, 'image_name': image_name, 'url': image_url})


@app.route('/fav', methods=['POST'])
def fav_image():
    user_id = request.json['user_id']
    image_id = request.json['image_id']
    s = Session(create_engine('sqlite:///account.db'))
    user = s.query(model.User).filter(model.User.id == user_id).first()
    image = s.query(model.Image).filter(model.Image.id == image_id).first()
    if image not in user.images:
        user.images.append(image)
        s.commit()
        return jsonify({'user_id': user.id, 'image_id': image.id, 'action': 'add' })
    else:
        user.images.remove(image)
        s.commit()
        return jsonify({'user_id': user.id, 'image_id': image.id, 'action': 'remove' })


@app.route('/delete', methods=['POST'])
def delete_image():
    image_id = request.json['image_id']
    s = Session(create_engine('sqlite:///account.db'))
    image = s.query(model.Image).filter(model.Image.id == image_id).first()
    image.active = False
    s.commit()
    return jsonify({'id': image.id, 'name': image.name })


@app.route('/disconnect')
def disconnect():
    session.clear()
    return jsonify({'success': True})


@app.route('/connect')
def connect():
    scope = request.args.get(
        'scope',
        'identify guilds')
    discord_session = make_session(scope=scope.split(' '))
    authorization_url, state = discord_session.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)


@app.route('/callback')
def callback():
    if request.values.get('error'):
        return request.values['error']
    discord_session = make_session(state=session.get('oauth2_state'))
    token = discord_session.fetch_token(
        TOKEN_URL,
        client_secret=OAUTH2_CLIENT_SECRET,
        authorization_response=request.url)
    session['oauth2_token'] = token
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run()
