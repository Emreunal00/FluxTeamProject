from flask import Flask, jsonify, request
import os

app = Flask(__name__)

user_data = {
    "username": "kullanici_adi",
    "email": "kullanici@example.com",
    "profile_image": None  # Varsayılan profil resmi
}

@app.route('/upload-profile-image', methods=['POST'])
def upload_profile_image():
    if 'profileImage' not in request.files:
        return jsonify({'success': False, 'message': 'No file part'})

    file = request.files['profileImage']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'})

    if file:
        # Dosya ismini oluştur ve kaydet
        filename = f"{user_data['username']}_profile.jpg"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Profil resmini kullanıcı bilgilerine kaydet
        user_data['profile_image'] = file_path
        return jsonify({'success': True, 'message': 'Profil resmi kaydedildi.', 'image_url': file_path})

@app.route('/get-user-profile', methods=['GET'])
def get_user_profile():
    # Kullanıcı bilgilerini döndür
    return jsonify({
        "username": user_data['username'],
        "email": user_data['email'],
        "profile_image": user_data['profile_image']
    })

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
