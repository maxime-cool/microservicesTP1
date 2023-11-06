from flask import Flask, render_template, request, jsonify, make_response
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3202
HOST = 'showtime'

with open('{}/databases/times.json'.format("."), "r") as jsf:
   schedule = json.load(jsf)["schedule"]

# add the route to the welcome page
@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Showtime service!</h1>"

# add the route to show all the schedule time
@app.route("/showtime", methods = ['GET'])
def get_schedule():
   res = make_response(jsonify(schedule),200)
   return res

# add the route to show the movies on date
@app.route("/showmovies/<date>", methods = ['GET'])
def get_movies_bydate(date):
   # search the date in database and return the reponse of movies at the date
   for elem in schedule:
      if str(elem["date"]) == str(date):
         res = make_response(jsonify(elem),200)
         return res
   
   res = make_response(jsonify({"error":"bad input parameter"}),400)
   return res



if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
