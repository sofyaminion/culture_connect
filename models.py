from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/sofya/PycharmProjects/git/.db'  # Путь к базе данных SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключение отслеживания изменений
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_active(self):
        return self.is_active

    def is_authenticated(self):
        # Реализуйте логику для определения аутентификации пользователя
        return True  # или False в зависимости от вашей логики

    def get_id(self):
        return self.id


class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)  # изменение на nullable=True

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Исправлено на 'users.id'
    bio = db.Column(db.Text)
    # Другие поля профиля, такие как фотография профиля и т. д.

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Исправлено на 'users.id'
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)  # Исправлено на 'events.id'

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Исправлено на 'users.id'
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Исправлено на 'users.id'
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

