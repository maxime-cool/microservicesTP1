from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3201
HOST = 'booking'

with open('{}/databases/bookings.json'.format("."), "r") as jsf:
    bookings = json.load(jsf)["bookings"]


@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

@app.route("/bookings", methods=["GET"])
def get_json():
    res = make_response(jsonify(bookings), 200)
    return res

# Get the booking information bu giving the user id
@app.route("/bookings/<userid>", methods=["GET"])
def get_booking_for_user(userid):
    for booking in bookings:
        if str(booking["userid"]) == str(userid):
            res = make_response(jsonify(booking), 200)
            return res
    res = make_response(jsonify({"error": "bookings not found for userid"}), 400)
    return res

# Add a new booking for the user by user id
@app.route("/bookings/<userid>", methods=["POST"])
def add_booking_byuser(userid):
    req = request.get_json()
    if not (req["date"] or req["movieid"]):  # request body does not have a date or a movieid
        return make_response(jsonify({"error": "incorrect request"}), 400)
    req_date, req_movie = req["date"], req["movieid"]
    booking_object = {"date": req_date, "movies": [req_movie]}
    if not movie_showing_on(req_date, req_movie):  # movie is not showing on date or error with showtime service
        return make_response(jsonify({"error": "movie or date not found"}))

    for user_bookings in bookings:
        if str(user_bookings["userid"]) == str(userid):  # if userid exists
            for day in user_bookings["dates"]:
                if str(day["date"]) == str(req_date):  # if user already has a booking on date
                    if req_movie in day["movies"]:  # if movie is already booked on this day
                        return make_response(jsonify({"error": "a similar booking already exists"}), 409)
                    day["movies"].append(req_movie)  # then add movie to existing list
                    index = bookings.index(user_bookings)
                    index1 = user_bookings["dates"].index(day)
                    bookings[index]["dates"][index1]["movies"].append(req_movie) 
                    save_file(bookings)
                    return make_response(jsonify(user_bookings), 200)

            user_bookings["dates"].append(booking_object)
            index = bookings.index(user_bookings)
            bookings[index]["dates"].append(booking_object)
            save_file(bookings)
            return make_response(jsonify(user_bookings), 200)

    # If user does not have any booking on this date, then we check that it exists and add user to DB
    bookings.append({
        "userid": userid,
        "dates": [booking_object]
    })
    save_file(bookings)
    return make_response(jsonify({"error": "userid is not found"}), 400)

# Function to save the changement in the booking database
def save_file(bookings):
    try:
        with open('{}/databases/bookings.json'.format("."), "w") as jsf:
            json.dump({"bookings": bookings}, jsf)
    except Exception as e:
        print(f"error when saving: {e}")


def movie_showing_on(date, movieid):  # returns True if movie is showing on date, False if not
    showing_on = requests.get(
        "http://showtime:3202/showmovies/" + str(date))  # we get the movies showing on requested date
    return not (showing_on.status_code != 200 or str(movieid) not in showing_on.json()["movies"])


if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT, debug=True)
