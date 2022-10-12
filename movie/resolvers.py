import json


# ---------- Queries ----------
def movie_with_id(_, info, _id):
    with open('{}/data/movies.json'.format("."), "r") as file:
        movies = json.load(file)['movies']
    for movie in movies:
        if movie['id'] == _id:
            return {'__typename': 'Movie'} | movie
    return {'__typename': 'QueryFailure', 'message': 'Movie not found!'}


def actor_with_id(_, info, _id):
    with open('{}/data/actors.json'.format("."), "r") as file:
        actors = json.load(file)['actors']
    for actor in actors:
        if actor['id'] == _id:
            return {'__typename': 'Actor'} | actor
    return {'__typename': 'QueryFailure', 'message': 'Actor not found!'}


def all_movies(_, info):
    with open('{}/data/movies.json'.format("."), "r") as file:
        return json.load(file)['movies']


def movie_with_title(_, info, _title):
    with open('{}/data/movies.json'.format("."), "r") as file:
        movies = json.load(file)['movies']
    for movie in movies:
        if movie['title'] == _title:
            return {'__typename': 'Movie'} | movie
    return {'__typename': 'QueryFailure', 'message': 'Movie not found!'}


def movies_above_rating(_, info, _rate):
    with open('{}/data/movies.json'.format("."), "r") as file:
        movies = json.load(file)['movies']
    res = []
    for movie in movies:
        if float(movie['rating']) >= float(_rate):
            res.append(movie)
    return res


def resolve_actors_in_movie(movie, info):
    with open('{}/data/actors.json'.format("."), "r") as file:
        actors = json.load(file)['actors']
        actors = [actor for actor in actors if movie['id'] in actor['films']]
        return actors


# ---------- Mutations ----------
def update_movie_rate(_, info, _id, _rate):
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)['movies']
    for movie in movies:
        if movie['id'] == _id:
            movie['rating'] = _rate
            with open('{}/data/movies.json'.format("."), "w") as wfile:
                json.dump({'movies': movies}, wfile)
            return {'__typename': 'Movie'} | movie
    return {'__typename': 'QueryFailure', 'message': 'Movie not found!'}


def create_movie(_, info, _id, _title, _director, _rate):
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)['movies']
    for movie in movies:
        if movie['id'] == _id:
            return {
                '__typename': 'QueryFailure',
                'message': 'Movie ID already exists!'
            }
    movie = {
        'id': _id,
        'title': _title,
        'director': _director,
        'rating': _rate,
    }
    movies.append(movie)
    with open('{}/data/movies.json'.format("."), "w") as wfile:
        json.dump({'movies': movies}, wfile)
    return {'__typename': 'Movie'} | movie


def delete_movie(_, info, _id):
    with open('{}/data/movies.json'.format("."), "r") as rfile:
        movies = json.load(rfile)['movies']
    for movie in movies:
        if movie['id'] == _id:
            movies.remove(movie)
            with open('{}/data/movies.json'.format("."), "w") as wfile:
                json.dump({'movies': movies}, wfile)
            return {'__typename': 'Movie'} | movie
    return {'__typename': 'QueryFailure', 'message': 'Movie not found!'}
