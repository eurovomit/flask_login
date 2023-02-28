import sqlite3

from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'you-will-never-guess'
manager = LoginManager(app)
# если пользователь не авторизован, его отправляют на другую страницу
manager.login_view = 'log_in'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/state')
# запрещаем доступ не авторизированным пользователям
@login_required
def state():
    return render_template('state.html')


@app.route('/log_in', methods=['GET', 'POST'])
def log_in():
    # если пользователь авторизован, он перенаправляется со страницы входа
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
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
            # если авторизация успешна - создаем пользователя для сессии, передаем кортеж записи из БД
            userlogin = User().create(line)
            # реализация флажка запомнить меня
            rm = True if request.form.get('checkbox') else False
            # заносим пользователя в сессию
            login_user(userlogin, remember=rm)
            # отправляем пользователя на страницу, на которую он хотел зайти еще не зарегитрированным
            return redirect(request.args.get('next') or url_for('profile'))
        else:
            return render_template('log_in.html')


@app.route('/profile')
@login_required
def profile():
    # current_user - специальная переменная пользователя класса User
    return render_template('profile.html', current_user_id=current_user.get_id())


# функция разавторизации
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('log_in'))


# обязательный класс с обязательными методами
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

    # создает переменную __user в которой кортеж записи из БД по id
    def create(self, user):
        self.__user = user
        return self

    # метод должен возвращать id пользователя, мы ее берем из созданной переменной __user
    def get_id(self):
        return str(self.__user[0])


# обязательный метод, обратный get_id из класса User
@manager.user_loader
def load_user(user_id):
    return User().fromDB(user_id)


if __name__ == '__main__':
    app.run(debug=True)
