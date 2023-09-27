from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound
import urllib3

urllib3.disable_warnings()

app = Flask(__name__)

# defining the server entry point
PORT = 3203
HOST = '0.0.0.0'

# open the database user
with open('{}/databases/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

# add the route for homepage of serveur user
@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the User service!</h1>"

# for users to access and use the booking server by id
@app.route("/user", methods = ['GET'])
def get_user_byid():
   # get the query parameter of user_id
   user_id = request.args.get("user_id")
   # get the query parameter of date
   date = request.args.get("date") 
   # get the query parameter of movieid
   movieid = request.args.get("movieid")
   data = {"date": date, "movieid": movieid}
   # check user existence
   user = next((user for user in users if str(user['id']) == str(user_id)), None)
   if user: # if exist, request for the booking using url
      url = "http://booking:3201/bookings/"+str(user_id)
      booking = requests.post(url, json=data)
      if booking.status_code == 200: # check the booking reponse and make reponse
        res = make_response(jsonify(booking.json()), booking.status_code)
      else:
        res = make_response(jsonify(booking.json()), booking.status_code)
   else:
      res = make_response(jsonify({"error":"user ID not found"}),400)
   return res

# for users to get the movies booking by id
@app.route("/user/booking/movies", methods=['GET'])
def get_user_booking_movies():
    # get the query parameter of user_id
    user_id = request.args.get("user_id")
    # check user existence
    user = next((user for user in users if user['id'] == user_id), None)
    if user: # if user exists, firstly go to the booking serveur to get the information of booking
        res = []
        bookings = requests.get("http://booking:3201/bookings/" + str(user_id), verify=False)
        if bookings.status_code != 200:
            return make_response(jsonify({"error": "user ID no bookings"}), 400)
        # if booking exists, next go to check every record of booking to get movies
        bookings_data = bookings.json()
        for elem in bookings_data["dates"]:
            info = {} # empty dict to store all the information of booking
            info["date"] = elem["date"]
            info["movies"] = [] 
            movies_id = elem["movies"]
            for id in movies_id:
                # visit the movie serveur to get the information of movie
                movie = requests.get("http://movie:3200/movies/" + str(id))
                if movie.status_code != 200: # check the movie existence
                    return make_response(jsonify({"error": "movies in booking not found"}), 400) #movie not exists, return 400
                info["movies"].append(movie.json()) 
            res.append(info)
        return make_response(jsonify(res), 200)
    else:
        return make_response(jsonify({"error": "user ID not found"}), 400)


if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)

