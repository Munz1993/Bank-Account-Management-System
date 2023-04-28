from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager


DIALECT = 'oracle'
SQL_DRIVER = 'cx_oracle'
USERNAME = 'project_106' #enter your username
PASSWORD = '106'
HOST = 'localhost'
PORT = 1521
SERVICE = 'orclpdb' # db service name
oracle_connection_string = DIALECT + '+' + SQL_DRIVER + '://' + USERNAME + ':' + PASSWORD +'@' + HOST + ':' + str(PORT) + '/?service_name=' + SERVICE

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'asdf1234'
    app.config['SQLALCHEMY_DATABASE_URI'] = oracle_connection_string
    app.config['SQLALCHEMY_POOL_SIZE'] = 5
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = 120
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 300 
    
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import Registry, Note
    
    with app.app_context():
        db.create_all()
        #db.drop_all()
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(ID):
        return Registry.query.get(int(ID))

    return app


