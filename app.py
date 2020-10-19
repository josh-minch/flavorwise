from flask import Flask, jsonify, render_template, request, session

import matrix


app = Flask(__name__)
app.config.from_object('config')
N_RECIPES = 20

@app.route("/")
def index():
    r_ingreds = recipes = cur_ingreds = None
    if 'cur_ingreds' in session:
        cur_ingreds = session['cur_ingreds']
        r_ingreds, recipes = matrix.search(cur_ingreds)

        r_ingreds = {k: r_ingreds[k] for k in list(r_ingreds)[:N_RECIPES]}
        recipes = recipes[:N_RECIPES]

    return render_template('index.html',
        r_ingreds = r_ingreds, recipes = recipes, cur_ingreds = cur_ingreds)


@app.route("/search", methods=["POST"])
def search():
    # TODO: Verify input
    input_ingred = request.form.get('search', 0, type=str).strip()
    cur_ingreds = append_session(input_ingred)
    return get_matrix_search(cur_ingreds)

@app.route("/remove", methods=["POST"])
def remove():
    ingreds_to_remove = request.form.keys()
    cur_ingreds = remove_session(ingreds_to_remove)
    return get_matrix_search(cur_ingreds)

def get_matrix_search(cur_ingreds):
    r_ingreds, recipes = matrix.search(cur_ingreds)
    result = ''
    for ingred in r_ingreds:
        result += '{} {}, '.format(ingred, r_ingreds[ingred])

    return jsonify(cur_ingreds=cur_ingreds, r_ingreds=result, recipes=recipes[:N_RECIPES])

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



