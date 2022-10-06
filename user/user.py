from collections import defaultdict
from datetime import datetime
from flask import Flask, request, jsonify, make_response
import grpc
import json
import requests

import booking_pb2
import booking_pb2_grpc

app = Flask(__name__)

BOOKING = 'localhost:3003'
MOVIE = 'http://localhost:3001/graphql'

with open('{}/data/users.json'.format("."), "r") as jsf:
    users = json.load(jsf)["users"]


@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the User service!</h1>"


@app.route('/users', methods=['GET'])
def get_users():
    return make_response(jsonify(users), 200)


@app.route('/users/<userid>', methods=['GET'])
def get_user_by_id(userid):
    for user in users:
        if str(user['id']) == str(userid):
            res = make_response(jsonify(user), 200)
            return res
    return make_response(jsonify({'error': 'User ID not found'}), 404)


@app.route('/users/<userid>', methods=['POST'])
def create_user(userid):
    for user in users:
        if str(user['id']) == str(userid):
            return make_response(jsonify({'error': 'user already exists'}), 409)

    body = request.get_json()
    name = body['name']

    user = {
        'id': userid,
        'name': name,
        'last_active': int(datetime.now().strftime('%Y%m%d')),
    }
    users.append(user)
    return make_response(jsonify(user), 201)


@app.route('/users/<userid>', methods=['PUT'])
def update_user(userid):
    body = request.get_json()
    for user in users:
        if str(user['id']) == str(userid):
            user['name'] = body.get('name', user['name'])
            user['last_active'] = body.get('last_active', user['last_active'])
            return make_response(jsonify(user), 200)

    return make_response(jsonify({'error': 'User ID not found'}), 404)


@app.route('/users/<userid>/bookings', methods=['GET'])
def get_user_bookings_by_id(userid):
    for user in users:
        if str(user['id']) == str(userid):
            break
    else:
        return make_response(jsonify({'error': 'User ID not found'}), 404)

    with grpc.insecure_channel(BOOKING) as channel:
        stub = booking_pb2_grpc.BookingStub(channel)
        userId = booking_pb2.UserId(userid=userid)
        response = stub.GetBookingByUserId(userId)
        bookings_by_date = response.booking.dates

    dates_by_movie = defaultdict(list)
    for booking in bookings_by_date:
        for movieid in booking.movies:
            dates_by_movie[movieid].append(booking.date)

    bookings = []
    query = """
query {{
    movie_with_id(_id: "{movieid}") {{
        id
        title
        rating
        director
    }}
}}
    """

    for movieid, dates in dates_by_movie.items():
        response = requests.post(MOVIE,
                                 json={'query': query.format(movieid=movieid)})
        movie = response.json()
        bookings.append(movie | {'dates': dates})

    return make_response(jsonify(bookings), 200)


if __name__ == "__main__":
    from argparse import ArgumentParser
    arg_parser = ArgumentParser()
    arg_parser.add_argument('-H', '--host', required=False)
    arg_parser.add_argument('-p', '--port', type=int, required=True)
    args = arg_parser.parse_args()

    print('Server running in port %s' % (args.port))
    app.run(host=args.host, port=args.port)
