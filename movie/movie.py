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
    res = make_response(jsonify(movies),200)
    return res

# Get movie by giving id
@app.route("/movies/<movieid>", methods=["GET"])
def get_movie_byid(movieid):
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            res = make_response(jsonify(movie), 200)
            return res
    return make_response(jsonify({"error":"Movie ID not found"}), 400)

# Get movie by giving the title
@app.route("/moviesbytitle", methods=['GET'])
def get_movie_bytitle():
    json = ""
    if request.args:
        req = request.args
        for movie in movies:
            if str(movie["title"]) == str(req["title"]):
                json = movie
    if not json:
        res = make_response(jsonify({"error":"movie title not found"}),400)
    else:
        res = make_response(jsonify(json),200)
    return res

#entry point to create a new film
@app.route("/movies/<movieid>", methods=['POST'])
def create_movie(movieid):
    req = request.get_json()
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            return make_response(jsonify({"error":"movie ID already exists"}),409)
    movies.append(req)
    with open('{}/databases/movies.json'.format("."), "w") as jsf:
        json.dump({"bookings": movies}, jsf)
    res = make_response(jsonify({"message":"movie added"}),200)
    return res

#entry point to update a film rate
@app.route("/movies/<movieid>/update_rating/<rate>", methods=['PUT'])
def update_movie_rating(movieid, rate):
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movie["rating"] = float(rate)
            with open('{}/databases/movies.json'.format("."), "w") as jsf:
                json.dump({"bookings": movies}, jsf)
            res = make_response(jsonify(movie),200)
            return res
    res = make_response(jsonify({"error":"movie ID not found"}),400)
    return res

#entry point to delete a film
@app.route("/movies/<movieid>", methods=['DELETE'])
def del_movie(movieid):
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movies.remove(movie)
            with open('{}/databases/movies.json'.format("."), "w") as jsf:
                json.dump({"bookings": movies}, jsf)
            return make_response(jsonify(movie),200)
    res = make_response(jsonify({"error":"movie ID not found"}),400)
    return res

#entry point to update a film title
@app.route("/movies/<movieid>/update_title/<title>", methods=["PUT"])
def change_title(movieid, title):
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movie["title"] = str(title)
            with open('{}/databases/movies.json'.format("."), "w") as jsf:
                json.dump({"bookings": movies}, jsf)
            return make_response(jsonify(movie), 200)
    res = make_response(jsonify({"error": "movie ID not found"}), 400)
    return res

if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT, debug=True)

