import model

import os
from flask import Flask, render_template, session, request, url_for, redirect, _request_ctx_stack
from requests_oauthlib import OAuth2Session

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

OAUTH2_CLIENT_ID = '443757232476258304'
# OAUTH2_CLIENT_ID = os.environ['OAUTH2_CLIENT_ID']
OAUTH2_CLIENT_SECRET = 'LCF32gCD-7s77co5Fnvak5A5b-yZ8Gk8'
# OAUTH2_CLIENT_SECRET = os.environ['OAUTH2_CLIENT_SECRET']
OAUTH2_REDIRECT_URI = 'http://localhost:5000/callback'

API_BASE_URL = os.environ.get('API_BASE_URL', 'https://discordapp.com/api')
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


def get_images():
    s = Session(create_engine('sqlite:///account.db'))
    return [image for image in s.query(model.Image).filter(model.Image.active)]


def is_tite_in_guilds(guilds):
    for guild in guilds:
        if guild['id'] == '202909295526805505':
            return guild
    return False


def has_permission(perm):
    return bool(perm & 0x10000000)


@app.route('/')
def index():
    discord = make_session(token=session.get('oauth2_token'))
    user = discord.get(API_BASE_URL + '/users/@me').json()
    guilds = discord.get(API_BASE_URL + '/users/@me/guilds').json()
    connections = discord.get(API_BASE_URL + '/users/@me/connections').json()
    print(user)
    if 'code' not in user:
        s = Session(create_engine('sqlite:///account.db'))
        if s.query(model.User).filter(model.User.id == user['id']).count() == 0:
            u = model.User(id=user['id'], username=user.username + '#' + user.discriminator, isInTite=bool(is_tite_in_guilds(guilds), hasEnougthRank=has_permission(is_tite_in_guilds(guilds)['permissions'])))
            print(u)
        return render_template('index.html', images=get_images(), user=user, is_tite=is_tite_in_guilds(guilds), has_perm=has_permission(is_tite_in_guilds(guilds)['permissions']))
    return render_template('index.html', images=get_images())


@app.route('/fav/<int:id>')
def fav_image(id):
    print(id)
    return redirect(url_for('index'))


@app.route('/delete/<int:id>')
def delete_image(id):
    print(id)
    s = Session(create_engine('sqlite:///account.db'))
    image = s.query(model.Image).filter(model.Image.id == id).first()
    image.active = False
    session.commit()
    return redirect(url_for('index'))


@app.route('/disconnect')
def disconnect():
    return redirect(url_for('index'))



@app.route('/connect')
def connect():
    scope = request.args.get(
        'scope',
        'identify guilds')
    discord = make_session(scope=scope.split(' '))
    authorization_url, state = discord.authorization_url(AUTHORIZATION_BASE_URL)
    session['oauth2_state'] = state
    return redirect(authorization_url)


@app.route('/callback')
def callback():
    if request.values.get('error'):
        return request.values['error']
    discord = make_session(state=session.get('oauth2_state'))
    token = discord.fetch_token(
        TOKEN_URL,
        client_secret=OAUTH2_CLIENT_SECRET,
        authorization_response=request.url)
    session['oauth2_token'] = token
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run()
