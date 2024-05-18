from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
# from flask_caching import Cache

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
# app.config['UPLOAD_FOLDER'] = '../static'
app.secret_key = 'secretkey qoguh[KMALBJNPJWO;KOQMNWL.LGJIQ;MW.LBNQ;FKMAg'

db = SQLAlchemy(app)
db.create_all()

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# cache = Cache()
# cache.init_app(app, config={'CACHE_TYPE': 'simple'})
