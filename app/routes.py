import configparser
import json
import sqlite3
import string
import random

import bcrypt
import flask_login
from flask import render_template, request, url_for, flash
from password_strength import PasswordPolicy
from werkzeug.utils import redirect

from app.db.database_attempts import database_attempts
from app.db.database_started_attempts import database_started_attempts
from app.db.user_db_connector import user_db_connector
from app import app
from app.logic.genetic_alg import crossover, mutate

server_adress = "http://localhost/"
base_path = "."

policy = PasswordPolicy.from_names(
    length=8,
    uppercase=1,
    numbers=1
)

start_mat = [
    [14, 11, 10, 9, 9, 10, 11, 14],
    [11, 8, 5, 4, 4, 5, 8, 11],
    [10, 5, 6, 3, 3, 6, 5, 10],
    [9, 4, 3, 4, 4, 3, 4, 9],
    [9, 4, 3, 4, 4, 3, 4, 9],
    [10, 5, 6, 3, 3, 6, 5, 10],
    [11, 8, 5, 4, 4, 5, 8, 11],
    [14, 11, 10, 9, 9, 10, 11, 14]
]

database_attempts.create_db()
database_started_attempts.create_db()
user_db_connector.create_db()

config = configparser.ConfigParser()
config.read(base_path + '/.conf')
user = config["USER_DATA"]['user']
user_name = config["USER_DATA"]['user_name']
password = config["USER_DATA"]["user_secret"]
smtp_server = config["SERVER_DATA"]["smtp_server"]
TLS_PORT = config["SERVER_DATA"]["TLS_PORT"]


class User(flask_login.UserMixin):
    pass


def get_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))


@app.route('/')
def landing():
    username = ""
    if flask_login.current_user.is_authenticated:
        username = user_db_connector.get_user_name_from_user_id(flask_login.current_user.id)
    return render_template('landing_page.html', title="Landing Page", game="", username=username)


@app.route('/login')
def login():
    return render_template('user/login.html', title="Login")


@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    user_password = request.form.get('password')

    if user_db_connector.login_user(username, user_password):
        user_entity = User()
        user_entity.id = user_db_connector.get_user_id_from_user_name(username)
        flask_login.login_user(user_entity)
        return redirect(url_for('home'))
    else:
        flash('wrong username or password')
        flask_login.logout_user()
        return redirect(url_for('login'))


@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))


@app.route('/register')
def register():
    return render_template('user/register.html', title="Register")


@app.route('/register', methods=['POST'])
def register_post():
    username = request.form.get('username')
    user_password = request.form.get('password')
    try:
        strength = policy.test(user_password)
        if len(strength) != 0:
            temp_string = "password too weak! "
            for i in range(len(strength)):
                temp_string += str(strength[i])
                temp_string += " "
            flash(temp_string)
            return redirect(url_for('register'))
        user_hash = get_random_string(32)
        user_id = user_db_connector.insert_user(username, user_password, user_hash)
        user_entity = User()
        user_entity.id = user_id
        flask_login.login_user(user_entity)
    except sqlite3.IntegrityError:
        print(username, "already exist")
        flask_login.logout_user()
    return redirect(url_for('home'))


@app.route('/home')
@flask_login.login_required
def home():
    user_id = flask_login.current_user.id
    username = user_db_connector.get_user_name_from_user_id(user_id)
    user_hash = user_db_connector.get_user_hash_from_user_id(user_id)
    return render_template('user/home.html', title="Register", username=username, hash=user_hash)


@app.route('/change_password')
@flask_login.login_required
def change_password():
    return render_template('user/change_password.html', title="Change Password")


@app.route('/change_password', methods=['POST'])
@flask_login.login_required
def change_password_put():
    user_id = flask_login.current_user.id
    old_password = request.form.get('old_password')

    encoded_old_password = old_password.encode('utf8')
    hashed_old_password = user_db_connector.get_password(user_id)
    if hashed_old_password is None:
        flash('wrong username or password')
        return redirect(url_for('change_password'))
    encoded_hashed_password = hashed_old_password.encode('utf8')
    if not bcrypt.checkpw(encoded_old_password, encoded_hashed_password):
        flash('wrong password')
        return redirect(url_for('change_password'))
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_new_password')
    if not new_password == confirm_new_password:
        flash('new passwords do not match')
        return redirect(url_for('change_password'))
    strength = policy.test(new_password)
    if len(strength) != 0:
        temp_string = "password too weak! "
        for i in range(len(strength)):
            temp_string += str(strength[i])
            temp_string += " "
        flash(temp_string)
        return redirect(url_for('change_password'))
    user_db_connector.edit_user(user_id, new_password)
    flash('changed password')
    return redirect(url_for('home'))


def delete_expred():
    exploieded = database_started_attempts.get_expired()
    if exploieded:
        for attempt in exploieded:
            database_started_attempts.delete_attempt_by_id(list(attempt)[0])


@app.route("/attempt/<attempt>")
def attempt(attempt):
    return "true " + attempt

@app.route("/started_attempt/<attempt>")
def started_attempt(attempt):
    return "true " + attempt

@app.route("/attempts/depth/<depth>")
def attempts(depth):
    games_amount = request.args.get("games_amount")
    username = request.args.get("username")
    attempts_of_user = database_attempts.get_attempts_with_username_from_querry(depth, games_amount, username)
    listed_attempts_of_user = []
    for attempt in attempts_of_user:
        listed_attempts_of_user.append(list(attempt))
    listed_attempts_of_user.sort(key=lambda x: x[4], reverse=True)

    started_attempts_of_user = database_started_attempts.get_attempts_with_username_from_querry(depth, games_amount, username)
    listed_started_attempts_of_user = []
    for attempt in started_attempts_of_user:
        attempt_temp = list(attempt)
        attempt_temp[5] = round(attempt_temp[5], 2)
        listed_started_attempts_of_user.append(attempt_temp)
        print(len(attempt_temp))
    return render_template('attempts/attempt_list.html', title="My_Attempts", attempt_list=listed_attempts_of_user,
                           started_attempt_list=listed_started_attempts_of_user)

@app.route("/attempts/all")
@flask_login.login_required
def all_attempts():
    delete_expred()
    attempts_of_user = database_attempts.get_attempts()
    listed_attempts_of_user = []
    char_attempts_scores = []
    char_attempts_trys = []
    for attempt in attempts_of_user:
        listed_attempts_of_user.append(list(attempt))
        if len(char_attempts_scores) == 0:
            char_attempts_scores.append(list(attempt)[4])
        else:
            char_attempts_scores.append(max(list(attempt)[4], char_attempts_scores[-1]))
        char_attempts_trys.append(len(char_attempts_scores))
    listed_attempts_of_user.sort(key=lambda x: x[4], reverse=True)

    started_attempts_of_user = database_started_attempts.get_attempts()
    listed_started_attempts_of_user = []
    if started_attempts_of_user:
        for attempt in started_attempts_of_user:
            attempt_temp = list(attempt)
            attempt_temp[5] = round(attempt_temp[5], 2)
            listed_started_attempts_of_user.append(attempt_temp)
            attempt_temp.append(round(attempt_temp[4]/attempt_temp[3]*100))


    return render_template('attempts/attempt_list.html', title="Attempts", attempt_list=listed_attempts_of_user, started_attempt_list=listed_started_attempts_of_user, char_attempts_scores=char_attempts_scores, char_attempts_trys=char_attempts_trys)



@app.route("/attempts/my")
@flask_login.login_required
def my_attempts():
    delete_expred()
    user_id = flask_login.current_user.id
    attempts_of_user = database_attempts.get_attempts_of_user(user_id)
    listed_attempts_of_user = []
    for attempt in attempts_of_user:
        listed_attempts_of_user.append(list(attempt))
    listed_attempts_of_user.sort(key=lambda x: x[4], reverse=True)

    started_attempts_of_user = database_started_attempts.get_attempts_of_user(user_id)
    listed_started_attempts_of_user = []
    if started_attempts_of_user:
        for attempt in started_attempts_of_user:
            attempt_temp = list(attempt)
            attempt_temp[5] = round(attempt_temp[5], 2)
            listed_started_attempts_of_user.append(attempt_temp)
            attempt_temp.append(round(attempt_temp[4]/attempt_temp[3]*100))


    return render_template('attempts/attempt_list.html', title="My_Attempts", attempt_list=listed_attempts_of_user, started_attempt_list=listed_started_attempts_of_user)


@app.route('/attempt', methods=['GET'])
def get_attempt():
    delete_expred()
    depth_int = int(request.args.get("depth"))
    games_amount = int(request.args.get("games_amount"))
    user_hash = request.args.get("hash")
    mutation_rate = float(request.args.get("mutation_rate"))
    crossover_rate = float(request.args.get("crossing_rate"))
    attempts = database_attempts.get_attemps_with_depth_amount(depth_int, games_amount)
    listes_attempts = []
    for attempt in attempts:
        listes_attempts.append(list(attempt))
    listes_attempts.sort(key=lambda x: x[5], reverse=True)
    if len(listes_attempts) == 0:
        matrix = start_mat
    else:
        matrix = json.loads(listes_attempts[0][8])
    unique = False
    while not unique:
        if len(listes_attempts) > 1:
            matrix = crossover(crossover_rate, matrix, json.loads(listes_attempts[1][8]))
        matrix = mutate(mutation_rate, matrix)
        if not database_attempts.get_attemps_with_matrix_depth_gameAmount(matrix, depth_int, games_amount):
            if not database_started_attempts.get_attemps_with_matrix_depth_gameAmount(matrix, depth_int, games_amount):
                unique = True
    attempt_id = database_started_attempts.insert_attempt(user_db_connector.get_user_id_by_hash(user_hash), depth_int, games_amount, matrix)
    gen = database_attempts.get_max_gen_from_ammount_and_depths(depth_int, games_amount)
    if not gen:
        gen = 0
    best_wr = 0
    if len(listes_attempts) > 0:
        best_wr = listes_attempts[0][5]
    returning = {"gen": int(gen)+1, "attempt_id": attempt_id, "mutated": matrix, "tiefe": depth_int, "games": games_amount, "staticmatrix": start_mat, "current_game": 0, "best_winrate": best_wr, "winrate": 0.0, "genericColor": "Black"}
    return json.dumps(returning)


@app.route('/attempt/update/<started_id>', methods=['POST'])
def update_attempt(started_id):

    delete_expred()
    started_attempt_id = int(started_id)
    user_hash = request.args.get("hash")
    current_game = int(request.args.get("current_game"))
    winrate = float(request.args.get("winrate"))
    user_id = user_db_connector.get_user_id_by_hash(user_hash)
    if user_id and database_started_attempts.is_users_started_attempt(started_attempt_id, user_id):
        database_started_attempts.update_expire_date_cg_winrate(started_attempt_id, current_game, winrate)
        return "okay"
    else:
        return 'no hash', 400


@app.route('/attempt/<started_id>', methods=['POST'])
def finished_attempt(started_id):

    delete_expred()
    json_payload = request.json
    score = float(json_payload['score'])
    aborted_game = int(json_payload['aborted_game'])
    games_json = json_payload['games_json']
    user_hash = json_payload['hash']
    started_attempt_id = int(started_id)

    user_id = user_db_connector.get_user_id_by_hash(user_hash)
    data = list(database_started_attempts.get_attempt_by_id(started_attempt_id)[0])
    database_started_attempts.delete_attempt_by_id(started_attempt_id)
    if user_id == data[1] and user_id:
        depth = data[2]
        games_amount = data[5]
        matrix = json.loads(data[7])
        return database_attempts.insert_attempt(user_id, depth, games_amount, score, aborted_game, matrix, games_json)
    else:
        return 'no hash', 400

@app.route('/best_mat/<depth>', methods=['GET'])
def best_mat(depth):
    temp_json = database_attempts.get_best_attemps_with_depth(depth)[0]
    returning = {"matrix": json.loads(temp_json[8]), "best_winrate": temp_json[5]}
    return json.dumps(returning)