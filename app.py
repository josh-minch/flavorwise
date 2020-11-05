import http
import random

from flask import Flask, jsonify, render_template, request, session

import matrix
from helper import get_json

app = Flask(__name__)
app.config.from_object('config')

ALL_INGREDS = [ingred.lower() for ingred in get_json('all_ingreds_filtered.json')]
N_RECIPES = 142
N_R_INGREDS = 60

# TODO: Move session storage from flask session to .js SessionStorage
#       Try render_template instead of js stuff? Just use js for fetch?
# Or even move that straight to html with method="POST" action="/search"?
#       Pagination of results
#       allow multiple inputs,
#       Emojis, anyone?


@app.route("/")
def index():
    if 'cur_ingreds' not in session:
        cur_ingreds = []
    elif len(session['cur_ingreds']) == 0:
        cur_ingreds = []
    else:
        cur_ingreds = session['cur_ingreds']

    r_ingreds, recipes = matrix.search(cur_ingreds)
    r_ingreds = list(r_ingreds.keys())[:N_R_INGREDS]

    random_ingred = random.choice(ALL_INGREDS)
    pattern = create_search_pattern()

    return render_template('index.html', all_ingreds=ALL_INGREDS,
                        random_ingred=random_ingred, pattern=pattern,
                        r_ingreds=r_ingreds, recipes=recipes[:N_RECIPES], cur_ingreds=cur_ingreds)


@app.route("/search", methods=["POST"])
def search():
    new_ingreds = request.form.get('search', 0, type=str).strip()

    if not valid_input(new_ingreds):
        return '', http.HTTPStatus.NO_CONTENT

    cur_ingreds = add_session_ingreds(new_ingreds)
    return update_front_end(cur_ingreds)

@app.route("/remove", methods=["POST"])
def remove():
    ingreds_to_remove = request.form.keys()
    cur_ingreds = remove_session_ingreds(ingreds_to_remove)
    return update_front_end(cur_ingreds)


def update_front_end(cur_ingreds):
    r_ingreds, recipes = matrix.search(cur_ingreds)

    return jsonify(cur_ingreds=cur_ingreds,
                   r_ingreds=list(r_ingreds)[:N_R_INGREDS],
                   recipes=recipes[:N_RECIPES])

def valid_input(input_ingred):
    if input_ingred.lower() in ALL_INGREDS:
        return True
    else:
        return False

def create_search_pattern():
    """Return regex search string that matches any ingredient."""
    ingreds_regex = []
    for ingred in ALL_INGREDS:
        # Acount for upper or lower case of each letter
        ingred_regex = ''.join(['[{}{}]'.format(c.upper(), c.lower()) for c in ingred])
        ingreds_regex.append(ingred_regex)

    pattern = '|'.join(ingreds_regex)
    return pattern


def add_session_ingreds(new_ingreds):
    if 'cur_ingreds' not in session or session['cur_ingreds'] is None:
        session['cur_ingreds'] = [new_ingreds]
    elif new_ingreds not in session['cur_ingreds']:
        session['cur_ingreds'].append(new_ingreds)
        session.modified = True
    return session['cur_ingreds']


def remove_session_ingreds(ingreds_to_remove):
    for ingred in ingreds_to_remove:
        if ingred in session['cur_ingreds']:
            session['cur_ingreds'].remove(ingred)
            session.modified = True
    return session['cur_ingreds']



