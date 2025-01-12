from flask import Blueprint, request, jsonify

movies_blueprint = Blueprint('movies', __name__)

# Sample movie data
movies = []

@movies_blueprint.route('/movies', methods=['GET'])
def get_movies():
    return jsonify(movies)

@movies_blueprint.route('/movies', methods=['POST'])
def add_movie():
    movie_data = request.json
    movies.append(movie_data)
    return jsonify({"message": "Movie added successfully"}), 201