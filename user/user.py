from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound
import urllib3

urllib3.disable_warnings()

app = Flask(__name__)

# Defining the server entry point
PORT = 3203
HOST = 'localhost'

# open the database user
with open('{}/databases/users.json'.format("."), "r") as jsf:
    users = json.load(jsf)["users"]


@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the User service!</h1>"


# an entry point to book for a specific user ID
@app.route("/user", methods=['POST'])
def book():
    # get the query parameter of user_id
    user_id = request.args.get("user_id")
    date = request.args.get("date")
    movie_id = request.args.get("movie_id")
    data = {"date": date, "movie_id": movie_id}
    user = next((user for user in users if str(user['id']) == str(user_id)), None)
    if user:  # If user exists, check the booking for user is avaible or not
        url = "http://localhost:3201/bookings/" + str(user_id)
        booking_request = requests.post(url, json=data)
        print(booking_request.text)
        return make_response(jsonify(booking_request.json()), booking_request.status_code)
    return make_response(jsonify({'error': 'ID does not match any user'}), 404)


def check_user_existence(userid):  # checks user existence
    user = next((user for user in users if str(user['id']) == str(userid)), None)
    if not user:
        return False
    else:
        return True


# an entry point for retrieving film information for a user's reservations
@app.route("/user/booking/movies", methods=['GET'])
def get_bookings_data():
    # get the query parameter of user_id
    user_id = request.args.get("user_id")
    # check user existence
    user = next((user for user in users if user['id'] == user_id), None)
    if user:  # if user exists, firstly go to the booking serveur to get the information of booking
        res = []
        bookings = requests.get("http://localhost:3201/bookings/" + str(user_id), verify=False)
        if bookings.status_code != 200:
            return make_response(jsonify({"error": "this user does not have bookings"}), 400)
        # if booking exists, next go to check every record of booking to get movies
        bookings_data = bookings.json()
        for elem in bookings_data["dates"]:
            info = {"date": elem["date"], "movies": []}
            movies_id = elem["movies"]
            for movie_id in movies_id:  # For every movie, get the details from the server movie
                movie = requests.get("http://localhost:3200/movies/by_id" + f'?id={movie_id}')
                if movie.status_code != 200:
                    return make_response(jsonify({"error": "movies in booking not found"}), 404)
                info["movies"].append(movie.json())
            res.append(info)
        return make_response(jsonify(res), 200)


@app.route("/<userid>/bookings", methods=['GET'])
def get_user_bookings(userid):  # retrieves bookings for a given user

    if not check_user_existence(userid):  # check user existence
        return make_response(jsonify({"error": "user ID not found"}), 400)

    bookings_req = requests.get(f"http://localhost:3201/bookings/{userid}")
    return make_response(jsonify(bookings_req.json()), bookings_req.status_code)

    # data = {"date": date, "movieid": movieid}
    # user = next((user for user in users if str(user['id']) == str(user_id)), None)
    # if not user:
    #     return make_response(jsonify({"error": "user ID not found"}), 400)
    # else:
    #     booking = requests.get(f"http://localhost:3201/bookings/{user_id}")
    #     print(booking.text)
    #     return make_response(jsonify(booking.json()), booking.status_code)


@app.route("/<user_id>/bookings_info", methods=['GET'])
def get_user_bookings_info(user_id):  # retrieve bookings information for a given user
    # get the query parameter of user_id

    user_bookings = get_user_bookings(user_id).json

    movies_dict = {}
    # we create a dictionary to store movies info in case one appear several times,
    # to avoid pinging the movie service
    for dates in user_bookings["dates"]:
        dates["movies_data"] = []
        for movie_id in dates["movies"]:
            # first, we retrieve the movie data
            if movie_id in movies_dict:
                movie_data = movies_dict["movie_id"]
            else:
                movie_data = requests.get(f"http://localhost:3200/movies/{movie_id}")
                movies_dict["movie_id"] = movie_data
            # then, we add a movies_data field in the "dates" object

            dates["movies_data"].append(movie_data)

    return jsonify(user_bookings)

    # user_id = request.args.get("user_id")
    # # check user existence
    # user = next((user for user in users if user['id'] == user_id), None)
    # if user:  # if user exists, firstly go to the booking serveur to get the information of booking
    #     res = []
    #     bookings = requests.get("http://localhost:3201/bookings/" + str(user_id), verify=False)
    #     if bookings.status_code != 200:
    #         return make_response(jsonify({"error": "user ID no bookings"}), 400)
    #     # if booking exists, next go to check every record of booking to get movies
    #     bookings_data = bookings.json()
    #     for elem in bookings_data["dates"]:
    #         info = {"date": elem["date"], "movies": []}
    #         movies_id = elem["movies"]
    #         for id in movies_id:
    #             movie = requests.get("http://localhost:3200/movies/" + str(id))
    #             if movie.status_code != 200:
    #                 return make_response(jsonify({"error": "movies in booking not found"}), 400)
    #             info["movies"].append(movie.json())
    #         res.append(info)
    #     return make_response(jsonify(res), 200)
    # else:
    #     return make_response(jsonify({"error": "user ID not found"}), 400)


if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT)
