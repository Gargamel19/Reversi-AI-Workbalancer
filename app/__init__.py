from flask import Flask
import flask_login

app = Flask(__name__)

from app import routes

secret = "steffenhatnenkleinen"

app.secret_key = secret

login_manager = flask_login.LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def load_user(user_id):
    user = User()
    user.id = user_id
    return user
