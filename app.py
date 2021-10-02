import http
import random
import os

from flask import Flask, jsonify, render_template, request, session
from whitenoise import WhiteNoise

import matrix
from helper import get_json

app = Flask(__name__)
app.config.from_object('config')
app.wsgi_app = WhiteNoise(app.wsgi_app, root=os.path.join(
    os.path.dirname(__file__), 'static'), prefix='static/')

VERSION_STR = '?v=0.66'
ALL_INGREDS = [ingred.lower()
               for ingred in get_json('./static/all_ingreds_filtered.json')]


# TODO:
#       Try render_template instead of js stuff? Just use js for fetch?
# Or even move that straight to html with method="POST" action="/search"?
#     - Get seperate JQuery source seperate from datatables bundle.
#       load JQuery first, then typeahead, then datatables
#       for faster load time.
#     - allow multiple inputs
#       Emojis, anyone?


@ app.route("/")
def index():
    init_session_vars()
    remove_invalid_session_ingreds()
    cur_ingreds = get_session_var('cur_ingreds')

    r_ingreds, recipes = matrix.get_recommended(cur_ingreds)

    random_ingred = random.choice(ALL_INGREDS)
    pattern = create_search_pattern()

    return render_template('index.html', version_str=VERSION_STR,
                           random_ingred=random_ingred, pattern=pattern,
                           r_ingreds=r_ingreds, recipes=recipes,
                           cur_ingreds=cur_ingreds)


@ app.route("/search", methods=["POST"])
def search():
    new_ingreds = request.form.get('search', 0, type=str).strip()

    if not validate_ingred(new_ingreds):
        return '', http.HTTPStatus.NO_CONTENT

    add_session_ingreds(new_ingreds)
    return get_frontend_json_data()


@ app.route("/add_dropdown_ingred", methods=["POST"])
def add_dropdown_ingred():
    new_ingred = request.form.get('ingred_to_add')
    add_session_ingreds(new_ingred)
    return get_frontend_json_data()


@ app.route("/remove", methods=["POST"])
def remove():
    ingreds_to_remove = request.form.keys()
    remove_session_ingreds(ingreds_to_remove)
    return get_frontend_json_data()


def get_frontend_json_data():
    cur_ingreds = get_session_var('cur_ingreds')
    r_ingreds, recipes = matrix.get_recommended(cur_ingreds)

    return jsonify(cur_ingreds=cur_ingreds,
                   r_ingreds=r_ingreds,
                   recipes=recipes)


def validate_ingred(ingred):
    if ingred.lower() in ALL_INGREDS:
        return True
    else:
        return False


def create_search_pattern():
    """Return regex search string that matches any ingredient."""
    ingreds_regex = []
    for ingred in ALL_INGREDS:
        # Acount for upper or lower case of each letter
        ingred_regex = ''.join(
            ['[{}{}]'.format(c.upper(), c.lower()) for c in ingred])
        ingreds_regex.append(ingred_regex)

    pattern = '|'.join(ingreds_regex)
    return pattern


def get_session_var(var_name):
    if var_name not in session or not var_name:
        value = []
    else:
        value = session[var_name]
    return value


def init_session_vars():
    if 'cur_ingreds' not in session:
        session['cur_ingreds'] = []


def add_session_ingreds(new_ingreds):
    if 'cur_ingreds' not in session or session['cur_ingreds'] is None:
        session['cur_ingreds'] = [new_ingreds]
    elif new_ingreds not in session['cur_ingreds']:
        session['cur_ingreds'].append(new_ingreds)
        session.modified = True


def remove_session_ingreds(ingreds_to_remove):
    """ Remove ingreds_to_remove from session cookie. """
    if isinstance(ingreds_to_remove, str):
        ingreds_to_remove = [ingreds_to_remove]

    for ingred in ingreds_to_remove:
        if ingred in session['cur_ingreds']:
            session['cur_ingreds'].remove(ingred)
            session.modified = True


def remove_invalid_session_ingreds():
    if 'cur_ingreds' not in session:
        return
    # Create a copy, otherwise removing elements in a loop will skip elements
    session_ingreds = session['cur_ingreds'].copy()
    for ingred in session_ingreds:
        if not validate_ingred(ingred):
            session['cur_ingreds'].remove(ingred)
            session.modified = True
