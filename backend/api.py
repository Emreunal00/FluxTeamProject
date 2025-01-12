from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Flask! This is accessible from the internet."

@app.route("/api/movies")
def get_movies():
    # Örnek bir film listesi
    movies = [
        {"title": "The Shawshank Redemption", "description": "Two imprisoned men bond over a number of years."},
        {"title": "The Godfather", "description": "The aging patriarch of an organized crime dynasty transfers control to his reluctant son."},
        {"title": "The Dark Knight", "description": "Batman raises the stakes in his war on crime."},
    ]
    return jsonify(movies)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
