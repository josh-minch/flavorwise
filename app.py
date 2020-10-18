from flask import Flask, jsonify, render_template, request, session

import matrix


app = Flask(__name__)
app.config.from_object('config')


@app.route("/")
def index():
    r_ingreds = recipes = cur_ingreds = None
    if 'cur_ingreds' in session:
        cur_ingreds = session['cur_ingreds']
        r_ingreds, recipes = matrix.search(cur_ingreds)
    return render_template('index.html',
        r_ingreds=r_ingreds, recipes=recipes, cur_ingreds=cur_ingreds)


@app.route("/search", methods=["POST"])
def search():
    # TODO: Verify input
    input_ingred = request.form.get("search", 0, type=str).strip()
    cur_ingreds = update_session(input_ingred)
    r_ingreds, recipes = matrix.search(cur_ingreds)

    result = ''
    for ingred in r_ingreds:
        result += '{} {}, '.format(ingred, r_ingreds[ingred])

    return jsonify(cur_ingreds=cur_ingreds, r_ingreds=result, recipes=recipes)


def update_session(input_ingred):
    if 'cur_ingreds' not in session or session['cur_ingreds'] is None:
        session['cur_ingreds'] = [input_ingred]
    elif input_ingred in session['cur_ingreds']:
        pass
    else:
        session['cur_ingreds'].append(input_ingred)
        session.modified = True

    return session['cur_ingreds']
