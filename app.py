from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import yaml
import requests
import json  # JSON verisini işlemek için eklenmiştir
import os
import random
from werkzeug.utils import secure_filename
from models import db  # Import the db instance
from models.user import User
from models.favorite import Favorite  # Import the Favorite model

app = Flask(__name__, static_folder='frontend')
app.secret_key = "your_secret_key"  # Session için gerekli olan secret_key
OMDB_API_KEY = "f91c77a2"  # OMDB API anahtarı
UPLOAD_FOLDER = 'frontend/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  # Veritabanı bağlantı URI'si
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Initialize the SQLAlchemy instance with the app

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

    # Aynı kullanıcı adı veya e-posta kontrolü
    for user in users:
        if user['username'] == username or user['email'] == email:
            return False

    # Yeni kullanıcıyı ekle
    new_user = {"username": username, "email": email, "password": password}
    users.append(new_user)
    save_users(users)
    return True

# Kullanıcı girişini kontrol et
def login_user(username, password):
    users = load_users()

    for user in users:
        if user['username'] == username and user['password'] == password:
            return True

    return False

# Kullanıcıyı güncelle
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

def get_random_movies():
    """`movies.txt` dosyasından rastgele filmleri seçer ve OMDB API'den detaylarını alır."""
    try:
        # movies.txt dosyasını aç ve film isimlerini listele
        with open("movies.txt", "r") as file:
            movie_titles = [line.strip() for line in file if line.strip()]  # Boş satırları çıkarır
    except FileNotFoundError:
        print("movies.txt dosyası bulunamadı! Lütfen dosyayı oluşturun ve film isimlerini ekleyin.")
        return []  # Eğer dosya yoksa, boş liste döndür

    # Film isimlerinden rastgele 10 tanesini seç
    random_movies = random.sample(movie_titles, min(len(movie_titles), 30))  # 10 veya daha az seçer
    recommended_movies = []

    for title in random_movies:
        response = requests.get(f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}")
        if response.status_code == 200:
            movie = response.json()

            # Eğer başlık veya poster bilgisi eksikse, filmi atla
            if not movie.get("Title") or not movie.get("Poster"):
                continue

            # Film verilerini ekle
            recommended_movies.append({
                "title": movie["Title"],
                "poster": movie["Poster"]
            })
            
    while len(recommended_movies) < 30:
        for title in random_movies:
            response = requests.get(f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}")
            if response.status_code == 200:
                movie = response.json()

                # Eğer başlık veya poster bilgisi eksikse, filmi atla
                if not movie.get("Title") or not movie.get("Poster"):
                    continue

                # Poster verisinin yüklenip yüklenmediğini kontrol et
                recommended_movies.append({
                    "title": movie["Title"],
                    "poster": movie["Poster"]
                })

            if len(recommended_movies) == 30:
                break

    return recommended_movies


@app.route('/')
def home():
    recommended_movies = get_random_movies()
    return render_template("dashboard.html", recommended_movies=recommended_movies)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if login_user(username, password):
            session['user'] = username  # Kullanıcıyı session'a ekle
            return redirect(url_for('dashboard'))
        else:
            return "Giriş başarısız! Kullanıcı adı veya şifre yanlış."
    
    return render_template("login.html")

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
    if 'user' not in session:  # Eğer oturum yoksa giriş sayfasına yönlendir
        return redirect(url_for('home'))
    recommended_movies = get_random_movies()
    return render_template("dashboard.html", recommended_movies=recommended_movies)

@app.route('/logout')
def logout():
    session.pop('user', None)  # Kullanıcıyı session'dan çıkar
    return redirect(url_for('login'))  # Login sayfasına yönlendir

@app.route('/profile')
def profile():
    if 'user' not in session:  # Eğer oturum yoksa giriş sayfasına yönlendir
        return redirect(url_for('home'))
    
    username = session['user']
    users = load_users()

    # Kullanıcıyı bul
    user_info = next((user for user in users if user['username'] == username), None)
    
    if user_info:
        return render_template(
            'profile.html',
            user_username=user_info['username'],
            user_email=user_info['email'],
            user_profile_image=user_info.get('profile_image', 'default_image.png')  # Varsayılan bir resim kullanılır
        )
    
    return "Kullanıcı bilgileri bulunamadı!"

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user' not in session:  # Eğer oturum yoksa giriş sayfasına yönlendir
        return redirect(url_for('home'))
    
    username = session['user']
    current_password = request.form['current-password']
    new_password = request.form['new-password']
    new_username = request.form['new-username']
    
    if update_user_info(username, new_username=new_username, new_password=new_password):
        session['user'] = new_username  # Oturumda güncellenmiş kullanıcı adı
        return redirect(url_for('profile'))  # Profil sayfasına yönlendir
    else:
        return "Kullanıcı bilgileri güncellenemedi!"  # Hata mesajı

# Filmler rotası
@app.route('/movies', methods=['GET', 'POST'])
def movies():
    if 'user' not in session:  # Eğer oturum yoksa giriş sayfasına yönlendir
        return redirect(url_for('home'))
    
    movie_data = []  # Film detaylarını saklamak için bir liste
    error_message = None  # Hata mesajını saklamak için değişken

    if request.method == 'POST':
        movie_name = request.form['movie_name']
        
        # İlk olarak `s` parametresi ile genel bir arama yapılıyor
        search_response = requests.get(f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={movie_name}")
        
        if search_response.status_code == 200:
            search_results = search_response.json()  # JSON verisini parse et
            
            if search_results.get('Response') == 'True':  # Eğer arama başarılıysa
                for movie in search_results.get('Search', []):  # Her film için
                    imdb_id = movie.get('imdbID')  # IMDb ID'sini al
                    if imdb_id:  # Eğer IMDb ID mevcutsa
                        # `t` parametresi yerine `i` (IMDb ID) kullanılarak detay bilgileri alınır
                        detail_response = requests.get(f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&i={imdb_id}")
                        
                        if detail_response.status_code == 200:
                            movie_details = detail_response.json()  # JSON verisini al
                            movie_data.append(movie_details)  # Film detaylarını listeye ekle
            else:
                error_message = "Aradığınız filme dair sonuç bulunamadı."
        else:
            error_message = "Film verisi alınamadı. Lütfen tekrar deneyin."
        
    return render_template('movies.html', movie_data=movie_data, error_message=error_message)

@app.route('/add_to_favorites', methods=['POST'])
def add_to_favorites():
    if 'user' not in session:
        return jsonify(success=False, message="Oturum açmanız gerekiyor."), 401
    
    username = session['user']
    movie_data = request.json.get('movie_data')  # Film bilgisini al

    # JSON verisini konsola yazdırarak kontrol edin
    print(f"Received movie_data: {movie_data}")
    
    try:
        # JSON verisini Python dict'e dönüştür
        movie_dict = json.loads(movie_data)
    except json.JSONDecodeError as e:
        # Hata mesajını konsola yazdır
        print(f"JSONDecodeError: {str(e)}")
        return jsonify(success=False, message=f"Geçersiz JSON verisi: {str(e)}"), 400
    
    # Check if the movie is already in the user's favorites
    existing_favorite = Favorite.query.filter_by(username=username, imdb_id=movie_dict['imdbID']).first()
    if not existing_favorite:
        # Add the movie to the user's favorites
        new_favorite = Favorite(
            username=username,
            imdb_id=movie_dict['imdbID'],
            title=movie_dict['Title'],
            year=movie_dict['Year'],
            genre=movie_dict['Genre'],
            director=movie_dict['Director'],
            actors=movie_dict['Actors'],
            plot=movie_dict['Plot'],
            poster=movie_dict['Poster'],
            imdb_rating=movie_dict['imdbRating']
        )
        db.session.add(new_favorite)
        db.session.commit()
        return jsonify(success=True, message="Film favorilere eklendi.")
    else:
        return jsonify(success=False, message="Film zaten favorilerinizde.")

# Favori filmleri gösterme
@app.route('/favorites')
def favorites():
    if 'user' not in session:
        return redirect(url_for('home'))
    
    username = session['user']
    favorite_movies = Favorite.query.filter_by(username=username).all()
    
    return render_template('favorites.html', favorite_movies=favorite_movies)

if __name__ == "__main__":
    app.run(debug=True)
