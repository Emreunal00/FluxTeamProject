from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):  # Flask-SQLAlchemy Modeli
    __tablename__ = 'users'  # Opsiyonel: Tablo adı

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    profile_image = db.Column(db.String(255), nullable=True)  # Profil resmi için dosya yolu

    def __init__(self, username, email, profile_image=None):
        self.username = username
        self.email = email
        self.profile_image = profile_image

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "profile_image": self.profile_image
        }
