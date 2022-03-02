import datetime
from flask import Flask, url_for, render_template, make_response, request, session, abort
from werkzeug.utils import redirect

from forms.loginform import LoginForm
from forms.news import NewsForm
from forms.user import RegisterForm
from data.news import News
from data.jobs import Jobs
from data.users import User
from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)


# @app.route("/")
# @app.route("/index")
# def index():
#     db_sess = db_session.create_session()
#     jobs = db_sess.query(Jobs).all()
#     return render_template("index.html", jobs=jobs)

@app.route("/")
@app.route("/index")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index2.html", news=news)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(
            f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie("visits_count", str(visits_count + 1),
                       max_age=60 * 60 * 24 * 365 * 2)
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года")
        res.set_cookie("visits_count", '1', max_age=60 * 60 * 24 * 365 * 2)
        res.set_cookie("name", "vasya", max_age=60 * 60 * 24 * 365 * 2)
        res.set_cookie("password", "durak", max_age=60 * 60 * 24 * 365 * 2)

    return res


@app.route("/session_test")
def session_test():
    visits_count = session.get('visits_count', 0)
    session['visits_count'] = visits_count + 1
    return make_response(
        f"Вы пришли на эту страницу {visits_count + 1} раз")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/success')
def success():
    return render_template("success.html")


@app.route('/promotion')
def promotion():
    return '''Человечество вырастает из детства.<br>
Человечеству мала одна планета.<br>
Мы сделаем обитаемыми безжизненные пока планеты.<br>
И начнем с Марса!<br>
Присоединяйся!'''


@app.route('/image_mars')
def image():
    return f"""<!doctype html>
                <html lang="en">
                  <head>
                    <meta charset="utf-8">
                    <title>Привет, Марс!</title>
                  </head>
                  <body>
                    <h1>Жди нас, Марс!</h1>
                    <img src="{url_for('static', filename='img/mars.jpg')}" 
                    alt="здесь должна была быть картинка, но не нашлась">
                    Вот она красная планета!
                  </body>
                </html>"""


def users_add():
    user1 = User()
    user1.surname = "Scott"
    user1.name = "Ridley"
    user1.age = 21
    user1.position = "captain"
    user1.speciality = "research engineer"
    user1.address = "module_1"
    user1.email = "scott_chief@mars.org"

    user2 = User()
    user2.surname = "Scoty"
    user2.name = "Red"
    user2.age = 13
    user2.position = "helper"
    user2.speciality = "doctor"
    user2.address = "module_1"
    user2.email = "scoty_doc@mars.org"

    user3 = User()
    user3.surname = "Bredly"
    user3.name = "Crug"
    user3.age = 25
    user3.position = "matros"
    user3.speciality = "research doctor"
    user3.address = "module_2"
    user3.email = "bredly_dadly@mars.org"

    user4 = User()
    user4.surname = "Jony"
    user4.name = "Cromwell"
    user4.age = 32
    user4.position = "matros"
    user4.speciality = "engineer"
    user4.address = "module_3"
    user4.email = "jony_syyns@mars.org"

    db_sess = db_session.create_session()
    db_sess.add(user1)
    db_sess.add(user2)
    db_sess.add(user3)
    db_sess.add(user4)
    db_sess.commit()


def jobs_add():
    job = Jobs()
    job.team_leader_id = 1
    job.job = "deployment of residential modules 1 and 2"
    job.work_size = 15
    job.collaborators = "2, 3"
    job.is_finished = False
    db_sess = db_session.create_session()
    db_sess.add(job)
    db_sess.commit()


def news_add():
    db_sess = db_session.create_session()
    news = News(title="Первая новость", content="Привет блог!",
                user_id=1, is_private=False)

    user = db_sess.query(User).filter(User.email == "email@email.ru").first()
    news2 = News(title="Вторая новость", content="Уже вторая запись!",
                 user=user, is_private=False)
    news3 = News(title="Первая новость", content="Привет блог!",
                 user_id=1, is_private=False)

    db_sess.add(news2)
    db_sess.add(news3)
    db_sess.commit()


def user_get():
    db_sess = db_session.create_session()
    # user = db_sess.query(User).filter(User.id == 1).first()
    for user in db_sess.query(User).all():
        print(user)


if __name__ == '__main__':
    # db_session.global_init("db/jobs.db")
    db_session.global_init("db/blogs.db")
    # users_add()
    # news_add()
    # user_get()
    # jobs_add()
    app.run(port=8080, host='127.0.0.1')
