import http
import random

from flask import Flask, jsonify, render_template, request, session

import matrix
from helper import get_json

app = Flask(__name__)
app.config.from_object('config')
N_RECIPES = 500
ALL_INGREDS = [ingred.lower() for ingred in get_json('all_ingreds_filtered.json')]

# TODO: Move session storage from flask session to .js SessionStorage
#       Try render_template instead of js stuff? Just use js for fetch?
# Or even move that straight to html with method="POST" action="/search"?
#       Pagination of results
#       Verify input, allow multiple inputs, dropdown search menu
#       Click to add ingreds
#       Fix js polyfill 404 (check browser console on load)
#       Emojis, anyone?


@app.route("/")
def index():
    r_ingreds = recipes = cur_ingreds = None
    if 'cur_ingreds' in session:
        cur_ingreds = session['cur_ingreds']
        r_ingreds, recipes = matrix.search(cur_ingreds)

        r_ingreds = {k: r_ingreds[k] for k in list(r_ingreds)[:N_RECIPES]}
        recipes = recipes[:N_RECIPES]

    random_ingred = random.choice(ALL_INGREDS)
    pattern = create_search_pattern()
    return render_template('index.html', all_ingreds=ALL_INGREDS, random_ingred=random_ingred, pattern=pattern,
        r_ingreds=r_ingreds, recipes=recipes, cur_ingreds=cur_ingreds)


@app.route("/search", methods=["POST"])
def search():
    # TODO: Verify input
    input_ingred = request.form.get('search', 0, type=str).strip()
    if not valid_input(input_ingred):
        return '', http.HTTPStatus.NO_CONTENT
    cur_ingreds = append_session(input_ingred)
    return get_matrix_search(cur_ingreds)

@app.route("/remove", methods=["POST"])
def remove():
    ingreds_to_remove = request.form.keys()
    cur_ingreds = remove_session(ingreds_to_remove)
    return get_matrix_search(cur_ingreds)


def valid_input(input_ingred):
    if input_ingred.lower() in ALL_INGREDS:
        return True
    else:
        return False


def create_search_pattern():
    """ Return regex search string that matches any ingredient. """
    ingreds_regex = []
    for ingred in ALL_INGREDS:
        ingred_regex = ''.join(['[{}{}]'.format(c.upper(), c.lower()) for c in ingred])
        ingreds_regex.append(ingred_regex)

    pattern = '|'.join(ingreds_regex)
    return pattern


def get_matrix_search(cur_ingreds):
    r_ingreds, recipes = matrix.search(cur_ingreds)

    return jsonify(cur_ingreds=cur_ingreds, r_ingreds=list(r_ingreds), recipes=recipes[:N_RECIPES])

def remove_session(ingreds):
    for ingred in ingreds:
        if ingred in session['cur_ingreds']:
            session['cur_ingreds'].remove(ingred)
            session.modified = True
    return session['cur_ingreds']

def append_session(input_ingred):
    if 'cur_ingreds' not in session or session['cur_ingreds'] is None:
        session['cur_ingreds'] = [input_ingred]
    elif input_ingred not in session['cur_ingreds']:
        session['cur_ingreds'].append(input_ingred)
        session.modified = True
    return session['cur_ingreds']



