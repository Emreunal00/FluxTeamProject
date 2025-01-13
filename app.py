from flask import Flask, render_template, request, redirect, url_for, session
import yaml
import requests
import json
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import ast

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Session için gerekli olan secret_key
OMDB_API_KEY = "f91c77a2"  # OMDB API anahtarı

# Veritabanı yapılandırması
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'  # SQLite veritabanı
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Movie modelini oluştur
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    year = db.Column(db.String(4), nullable=False)
    rated = db.Column(db.String(10), nullable=False)
    released = db.Column(db.Date)
    runtime = db.Column(db.String(50))
    genre = db.Column(db.String(100))
    director = db.Column(db.String(255))
    writer = db.Column(db.String(255))
    actors = db.Column(db.Text)
    plot = db.Column(db.Text)
    language = db.Column(db.String(255))
    country = db.Column(db.String(255))
    awards = db.Column(db.String(255))
    poster_url = db.Column(db.String(255))
    imdb_rating = db.Column(db.Float)
    imdb_votes = db.Column(db.String(50))
    imdb_id = db.Column(db.String(50))
    box_office = db.Column(db.String(50))
    username = db.Column(db.String(50), nullable=False)

# Veritabanını oluştur (ilk çalıştırmada)
with app.app_context():
    db.create_all()

# Kullanıcıları YAML dosyasından oku
def load_users():
    with open("users.yaml", "r") as file:
        data = yaml.safe_load(file)
        return data['users']

# Kullanıcıları YAML dosyasına kaydet
def save_users(users):
    with open("users.yaml", "w") as file:
        yaml.dump({"users": users}, file)

# Kullanıcı kaydını yap
def register_user(username, email, password):
    users = load_users()

    for user in users:
        if user['username'] == username or user['email'] == email:
            return False

    new_user = {"username": username, "email": email, "password": password}
    users.append(new_user)
    save_users(users)
    return True

def login_user(username, password):
    users = load_users()
    for user in users:
        if user['username'] == username and user['password'] == password:
            return True
    return False

def update_user_info(username, new_username=None, new_password=None):
    users = load_users()
    for user in users:
        if user['username'] == username:
            if new_username:
                user['username'] = new_username
            if new_password:
                user['password'] = new_password
            save_users(users)
            return True
    return False

def load_favorites(username):
    movies = Movie.query.filter_by(username=username).all()
    return movies

def save_favorites(username, movie_data):
    new_movie = Movie(
        title=movie_data['Title'],
        year=movie_data['Year'],
        rated=movie_data['Rated'],
        released=datetime.strptime(movie_data['Released'], '%d %b %Y'),
        runtime=movie_data['Runtime'],
        genre=movie_data['Genre'],
        director=movie_data['Director'],
        writer=movie_data['Writer'],
        actors=movie_data['Actors'],
        plot=movie_data['Plot'],
        language=movie_data['Language'],
        country=movie_data['Country'],
        awards=movie_data['Awards'],
        poster_url=movie_data['Poster'],
        imdb_rating=float(movie_data['imdbRating']),
        imdb_votes=movie_data['imdbVotes'],
        imdb_id=movie_data['imdbID'],
        box_office=movie_data['BoxOffice'],
        username=username
    )

    db.session.add(new_movie)
    db.session.commit()

@app.route('/')
def home():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if login_user(username, password):
        session['user'] = username
        return redirect(url_for('dashboard'))
    else:
        return "Giriş başarısız! Kullanıcı adı veya şifre yanlış."

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if register_user(username, email, password):
            return redirect(url_for('home'))
        else:
            return "Kullanıcı adı veya e-posta zaten kayıtlı."
    return render_template("register.html")

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('home'))
    return render_template("dashboard.html")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect(url_for('home'))
    username = session['user']
    users = load_users()
    user_info = next((user for user in users if user['username'] == username), None)
    if user_info:
        return render_template(
            'profile.html',
            user_username=user_info['username'],
            user_email=user_info['email'],
            user_profile_image=user_info.get('profile_image', 'default_image.png')
        )
    return "Kullanıcı bilgileri bulunamadı!"

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user' not in session:
        return redirect(url_for('home'))
    username = session['user']
    current_password = request.form['current-password']
    new_password = request.form['new-password']
    new_username = request.form['new-username']
    if update_user_info(username, new_username=new_username, new_password=new_password):
        session['user'] = new_username
        return redirect(url_for('profile'))
    else:
        return "Kullanıcı bilgileri güncellenemedi!"

@app.route('/movies', methods=['GET', 'POST'])
def movies():
    if 'user' not in session:
        return redirect(url_for('home'))
    movie_data = None
    if request.method == 'POST':
        movie_name = request.form['movie_name']
        response = requests.get(f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={movie_name}")
        if response.status_code == 200:
            movie_data = response.json()
        else:
            return "Film verisi alınamadı.", 400
    return render_template('movies.html', movie_data=movie_data)

@app.route('/add_to_favorites', methods=['POST'])
def add_to_favorites():
    movie_data = request.form.get('movie_data')

    try:
        # Tek tırnaklı veriyi çift tırnaklı JSON formatına çevir
        if movie_data:
            movie_data = ast.literal_eval(json.dumps(movie_data))
            movie_dict = json.loads(movie_data)

            # Favorilere ekleme işlemi
            save_favorites(session['user'], movie_dict)
    except Exception as e:
        print("Veri hatası:", e)
        return f"Hata: {e}", 400

    return redirect(url_for('favorites'))

@app.route('/favorites')
def favorites():
    if 'user' not in session:
        return redirect(url_for('home'))
    username = session['user']
    favorite_movies = load_favorites(username)
    return render_template('favorites.html', favorite_movies=favorite_movies)

if __name__ == "__main__":
    app.run(debug=True)
