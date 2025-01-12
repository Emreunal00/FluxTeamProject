from flask import Flask, jsonify

app = Flask(__name__)

# Sample movie data
movies = [
    {"title": "Inception", "description": "A mind-bending thriller about dreams within dreams."},
    {"title": "The Matrix", "description": "A hacker learns the truth about the nature of reality."},
    {"title": "The Dark Knight", "description": "Batman faces off against the Joker in Gotham City."},
]

@app.route('/api/movies')
def get_movies():
    # Return movies as JSON response
    return jsonify(movies)

if __name__ == "__main__":
    app.run(debug=True)