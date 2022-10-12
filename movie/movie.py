from ariadne import (graphql_sync, make_executable_schema,
                     load_schema_from_path, ObjectType, QueryType, MutationType)
from ariadne.constants import PLAYGROUND_HTML
from flask import Flask, request, jsonify, make_response
import resolvers as r

PORT = 3301
HOST = '0.0.0.0'
app = Flask(__name__)

type_defs = load_schema_from_path('movie.graphql')
query = QueryType()
movie = ObjectType('Movie')
query.set_field('movie_with_id', r.movie_with_id)

mutation = MutationType()
mutation.set_field('update_movie_rate', r.update_movie_rate)

actor = ObjectType('Actor')
movie.set_field('actors', r.resolve_actors_in_movie)
query.set_field('actor_with_id', r.actor_with_id)

query.set_field('all_movies', r.all_movies)
mutation.set_field('create_movie', r.create_movie)
mutation.set_field('delete_movie', r.delete_movie)
query.set_field('movie_with_title', r.movie_with_title)
query.set_field('movies_above_rating', r.movies_above_rating)

schema = make_executable_schema(type_defs, movie, query, mutation, actor)
###


# root message
@app.route("/", methods=['GET'])
def home():
    return make_response(
        "<h1 style='color:blue'>Welcome to the Movie service!</h1>", 200)


#####
# graphql entry points


@app.route('/graphql', methods=['GET'])
def playground():
    return PLAYGROUND_HTML, 200


@app.route('/graphql', methods=['POST'])
def graphql_server():
    success, result = graphql_sync(schema,
                                   request.get_json(),
                                   context_value=None,
                                   debug=app.debug)
    status_code = 200 if success else 400
    return jsonify(result), status_code


if __name__ == "__main__":
    print("Server running in port %s" % (PORT))
    app.run(host=HOST, port=PORT)
