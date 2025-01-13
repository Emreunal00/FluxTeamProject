from flask import Flask, render_template, request, redirect, url_for, session
import yaml
import requests
import json  # JSON verisini işlemek için eklenmiştir
from flask_sqlalchemy import SQLAlchemy
from backend.models.user import db, User

app = Flask(__name__, static_folder='frontend')
app.secret_key = "your_secret_key"  # Session için gerekli olan secret_key
OMDB_API_KEY = "f91c77a2"  # OMDB API anahtarı

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

# Kullanıcının favori filmlerini almak için
def load_favorites(username):
    users = load_users()
    user = next((user for user in users if user['username'] == username), None)
    
    if user and 'favorites' in user:
        return user['favorites']
    return []

# Kullanıcının favori filmlerini kaydetmek için
def save_favorites(username, favorites):
    users = load_users()
    user = next((user for user in users if user['username'] == username), None)
    
    if user:
        user['favorites'] = favorites
        save_users(users)

@app.route('/')
def home():
    return render_template("login.html")

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if login_user(username, password):
        session['user'] = username  # Kullanıcıyı session'a ekle
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
    if 'user' not in session:  # Eğer oturum yoksa giriş sayfasına yönlendir
        return redirect(url_for('home'))
    return render_template("dashboard.html")

@app.route('/logout')
def logout():
    session.pop('user', None)  # Kullanıcıyı session'dan çıkar
    return redirect(url_for('home'))  # Login sayfasına yönlendir

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
        return redirect(url_for('home'))
    
    username = session['user']
    movie_data = request.form['movie_data']  # Film bilgisini al

    # JSON verisini konsola yazdırarak kontrol edin
    print(f"Received movie_data: {movie_data}")
    
    try:
        # JSON verisini Python dict'e dönüştür
        movie_dict = json.loads(movie_data)
    except json.JSONDecodeError as e:
        # Hata mesajını konsola yazdır
        print(f"JSONDecodeError: {str(e)}")
        return f"Geçersiz JSON verisi: {str(e)}", 400  # Hata mesajı döndür
    
    favorites = load_favorites(username)
    # Favorilere eklenmiş mi kontrol et
    if not any(fav['imdbID'] == movie_dict['imdbID'] for fav in favorites):
        favorites.append(movie_dict)
        save_favorites(username, favorites)
    
    return redirect(url_for('favorites'))  # Favoriler sayfasına yönlendir

# Favori filmleri gösterme
@app.route('/favorites')
def favorites():
    if 'user' not in session:
        return redirect(url_for('home'))
    
    username = session['user']
    favorite_movies = load_favorites(username)
    
    return render_template('favorites.html', favorite_movies=favorite_movies)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'  # Veritabanı bağlantı URI'si
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

if __name__ == "__main__":
    app.run(debug=True)
