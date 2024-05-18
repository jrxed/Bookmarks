from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

from .init_app import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(40), unique=True, nullable=False)
    username = db.Column(db.String(40))
    password_hash = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    profile_pic_name = db.Column(db.String(80))
    next_card_index = db.Column(db.Integer, nullable=False)
    cards = db.Column(db.JSON)


class Card(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer)
    owner = db.Column(db.String(40))
    title = db.Column(db.String(40))
    link = db.Column(db.String(200))
    description = db.Column(db.String(200))
    preview_name = db.Column(db.String(80))
    url_hash = db.Column(db.String(80))


class Img(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(80))
    image = db.Column(db.LargeBinary)


db.create_all()
