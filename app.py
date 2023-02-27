import sqlite3

from flask_login import LoginManager, UserMixin, login_user, login_required

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
manager = LoginManager(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/state')
@login_required
def state():
    return render_template('state.html')


@app.route('/log_in', methods=['GET', 'POST'])
def log_in():
    if request.method == 'GET':
        return render_template('log_in.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        con = sqlite3.connect('test.db')
        cur = con.cursor()
        col = cur.execute('SELECT * FROM user WHERE name = ?', (username,))
        line = col.fetchone()
        con.close()
        if line and str(line[2]) == str(password):
            userlogin = User().create(line)
            login_user(userlogin)
            return redirect(url_for('index'))
        else:
            return render_template('log_in.html')


class User(UserMixin):
    def __init__(self):
        self.__user = None

    def fromDB(self, user_id):
        con = sqlite3.connect('test.db')
        cur = con.cursor()
        col = cur.execute(f'SELECT * FROM user WHERE id = {user_id}')
        self.__user = col.fetchone()
        con.close()
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user[0])


@manager.user_loader
def load_user(user_id):
    return User().fromDB(user_id)


if __name__ == '__main__':
    app.run(debug=True)
