from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound
import urllib3

urllib3.disable_warnings()

app = Flask(__name__)

# Defining the server entry point
PORT = 3203
HOST = '0.0.0.0'

# open the database user
with open('{}/databases/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/user", methods = ['GET'])
def get_user_byid():
   # get the query parameter of user_id
   user_id = request.args.get("user_id")
   date = request.args.get("date")
   movieid = request.args.get("movieid")
   data = {"date": date, "movieid": movieid}
   user = next((user for user in users if str(user['id']) == str(user_id)), None)
   if user:
      url = "http://booking:3201/bookings/"+str(user_id)
      booking = requests.post(url, json=data)
      print(booking.text)
      if booking.status_code == 200:
        res = make_response(jsonify(booking.json()), booking.status_code)
      else:
        res = make_response(jsonify(booking.json()), booking.status_code)
   else:
      res = make_response(jsonify({"error":"user ID not found"}),400)
   return res

@app.route("/user/booking/movies", methods=['GET'])
def get_user_booking_movies():
    user_id = request.args.get("user_id")
    user = next((user for user in users if user['id'] == user_id), None)
    if user:
        res = []
        bookings = requests.get("http://booking:3201/bookings/" + str(user_id), verify=False)
        if bookings.status_code != 200:
            return make_response(jsonify({"error": "user ID no bookings"}), 400)

        bookings_data = bookings.json()
        for elem in bookings_data["dates"]:
            info = {}
            info["date"] = elem["date"]
            info["movies"] = []
            movies_id = elem["movies"]
            for id in movies_id:
                movie = requests.get("http://movie:3200/movies/" + str(id))
                if movie.status_code != 200:
                    return make_response(jsonify({"error": "movies in booking not found"}), 400)
                info["movies"].append(movie.json())
            res.append(info)
        return make_response(jsonify(res), 200)
    else:
        return make_response(jsonify({"error": "user ID not found"}), 400)


if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)

