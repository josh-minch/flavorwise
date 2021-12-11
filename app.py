from flask import Flask, jsonify, render_template, request, session
from flask_talisman import Talisman

import backend

VERSION_STR = '?v=0.76'
''' Max number of recipes returned to users client '''
NUM_RECIPES = 40

app = Flask(__name__)
app.config.from_object('config')
Talisman(app, content_security_policy=None)


@ app.route("/")
def index():
    init_session_vars()
    remove_invalid_session_ingreds()
    cur_ingreds = get_session_var('cur_ingreds')

    random_ingreds = backend.get_random_ingreds(3)

    return render_template('index.html', version_str=VERSION_STR,
                           random_ingreds=random_ingreds,
                           cur_ingreds=cur_ingreds)


@ app.route('/init_r_ingred_data', methods=['GET'])
def init_r_ingred_data():
    cur_ingreds = get_session_var('cur_ingreds')
    r_ingreds = backend.get_r_ingreds(cur_ingreds)
    return jsonify(r_ingreds)


@ app.route('/init_recipe_data', methods=['GET'])
def init_recipe_data():
    cur_ingreds = get_session_var('cur_ingreds')
    recipes = backend.get_recipes(cur_ingreds)[:NUM_RECIPES]
    return jsonify(recipes)


@ app.route('/add', methods=['POST'])
def get_cur_ingreds():
    cur_ingreds = get_session_var('cur_ingreds')
    ingred_to_add = request.form.get('add')

    if ingred_to_add:
        add_session_ingreds(ingred_to_add)

    return jsonify(cur_ingreds)


@ app.route('/remove', methods=['POST'])
def remove():
    ingreds_to_remove = request.form.keys()
    remove_session_ingreds(ingreds_to_remove)
    cur_ingreds = get_session_var('cur_ingreds')
    return jsonify(cur_ingreds)


@ app.route('/get_table_data', methods=['POST'])
def search():
    cur_ingreds = get_session_var('cur_ingreds')
    r_ingreds, recipes = backend.get_recommended(cur_ingreds)

    return jsonify(r_ingreds=r_ingreds,
                   recipes=recipes[:NUM_RECIPES])


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
        if not backend.validate_ingred(ingred):
            session['cur_ingreds'].remove(ingred)
            session.modified = True
