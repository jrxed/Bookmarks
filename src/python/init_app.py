from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
# from flask_caching import Cache

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

application = Flask(__name__, template_folder='../templates', static_folder='../static')
application.app_context().push()
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'
# application.config['UPLOAD_FOLDER'] = '../static'
application.secret_key = 'secretkey qoguh[KMALBJNPJWO;KOQMNWL.LGJIQ;MW.LBNQ;FKMAg'

db = SQLAlchemy(application)
db.create_all()

bcrypt = Bcrypt(application)

login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'login'

# cache = Cache()
# cache.init_app(application, config={'CACHE_TYPE': 'simple'})
