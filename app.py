from flask import Flask, render_template, request, redirect, url_for, session
import yaml

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Session için gerekli olan secret_key

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

if __name__ == "__main__":
    app.run(debug=True)
