from flask import Flask, jsonify, render_template, request

from matrix import get_similar_ingreds_np

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('main.html')


@app.route("/search", methods=["POST"])
def search():
    ingred = request.form.get("a", 0, type=str)
    ingreds = get_similar_ingreds_np(ingred)[:100]
    result = ''
    for ingred in ingreds:
        result += '{}, '.format(ingred)

    return jsonify(result=result)
