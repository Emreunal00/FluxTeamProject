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

@movies_blueprint.route('/api/favorites', methods=['GET', 'POST'])
def manage_favorites():
    global favorites

    if request.method == 'POST':
        movie = request.json.get('movie')
        if not movie:
            return jsonify({'success': False, 'message': 'Film bilgisi eksik!'}), 400
        
        # Favorilere ekle
        if movie not in favorites:
            favorites.append(movie)
            return jsonify({'success': True, 'message': 'Film favorilere eklendi!', 'favorites': favorites})
        else:
            return jsonify({'success': False, 'message': 'Film zaten favorilerde!'}), 400

    # GET isteği ile favorileri listeleme
    return jsonify({'success': True, 'favorites': favorites})