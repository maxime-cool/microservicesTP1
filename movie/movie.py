from flask import Flask, render_template, request, jsonify, make_response
import json
import sys
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3200
HOST = 'localhost'

with open('{}/databases/movies.json'.format("."), "r") as jsf:
    movies = json.load(jsf)["movies"]


# root message
@app.route("/", methods=["GET"])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>", 200)


@app.route("/template", methods=["GET"])
def template():
    return make_response(render_template('index.html',
                                         body_text='This is my HTML template for Movie Service'), 200)


@app.route("/json", methods=["GET"])
def get_json():
    res = make_response(jsonify(movies), 200)
    return res


# checks that a request's body has the minimum data (every movie has an id)
def correct_movie_payload(req):
    json = req.get_json()
    return json and json["id"]


# Get movie by giving id
@app.route("/movies/by_id", methods=["GET"])
def get_movie_by_id():
    args = request.args
    movie_id = args.get("id", default="", type=str)
    if movie_id:
        for movie in movies:
            if str(movie["id"]) == str(movie_id):
                return make_response(jsonify(movie), 200)
    return make_response(jsonify({"error": "movie id not found"}), 400)


# Get movie by giving the title
@app.route("/movies/by_title", methods=['GET'])
def get_movie_by_title():
    args = request.args
    movie_title = args.get("title", default="", type=str)
    if movie_title:
        for movie in movies:
            if str(movie["title"]) == str(movie_title):
                return make_response(jsonify(movie), 200)
    return make_response(jsonify({"error": "movie title not found"}), 400)


# entry point to create a new film
@app.route("/movies/update", methods=['POST'])
def add_movie():
    if not correct_movie_payload(request):
        return make_response(jsonify({"error": "incorrect body format"}), 400)

    body = request.get_json()

    for movie in movies:
        if str(movie["id"]) == str(body["id"]):
            return make_response(jsonify({"error": "a movie with the same ID already exists"}), 409)

    movies.append(body)
    with open('{}/databases/movies.json'.format("."), "w") as jsf:
        json.dump({"movies": movies}, jsf)
    return make_response(jsonify({"message": "movie added"}), 200)


# entry point to delete a film
@app.route("/movies/update", methods=['DELETE'])
def del_movie():
    body = request.get_json()

    if not body["id"]:
        return make_response(jsonify({"error": "incorrect body format"}), 400)

    for movie in movies:
        if str(movie["id"]) == str(body["id"]):
            movies.remove(movie)
            with open('{}/databases/movies.json'.format("."), "w") as jsf:
                json.dump({"movies": movies}, jsf)
            return make_response(jsonify(movie), 200)

    return make_response(jsonify({"error": "ID does not match any film"}), 404)


# entry point to update film data
@app.route("/movies/update", methods=['PUT'])
def update_movie_data():
    if not correct_movie_payload(request):
        return make_response(jsonify({"error": "incorrect body format"}), 400)

    body = request.get_json()

    for movie in movies:
        if str(movie["id"]) == str(body["id"]):
            for key in body:
                movie[key] = body[key]
            with open('{}/databases/movies.json'.format("."), "w") as jsf:
                json.dump({"movies": movies}, jsf)
            return make_response(jsonify(movie), 200)

    return make_response(jsonify({"error": "ID does not match any film"}), 404)


if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT, debug=True)

