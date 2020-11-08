import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask import request
from flask_msearch import Search
from flask_bootstrap import Bootstrap
app = Flask(__name__)
app.config['SECRET_KEY']= 'c345da661f036e558615f63765abe071'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site2.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'btd13sadm@gmail.com'
app.config['MAIL_PASSWORD'] = 'sadm12345'
mail = Mail(app)
search = Search(app)
search.init_app(app)
search.create_index(update=True)
MSEARCH_INDEX_NAME =  os.path.join(app.root_path,'msearch')
MSEARCH_PRIMARY_KEY = 'id'
MSEARCH_ENABLE = True
SQLALCHEMY_TRACK_MODIFICATIONS = True
bootstrap = Bootstrap(app)












from sadm import routes