from flask import Flask, render_template, redirect, request, abort
from forms.loginform import LoginForm
import locale
from data.users import User
from forms.registerform import RegisterForm
from data import db_session
from data.themes import Theme
from forms.themesform import ThemesForm
from forms.profileform import ProfileForm
from flask_login import login_user, LoginManager, current_user, login_required, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
locale.setlocale(
    category=locale.LC_ALL,
    locale="ru_RU.utf8"
)

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/blogs.db")

    port = 5000
    app.run(host='127.0.0.1', port=port)


@app.errorhandler(500)
def notfound(e):
    return render_template("error404.html")


@app.errorhandler(404)
def notfound2(e):
    return render_template("error404.html")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


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


@app.route('/register', methods=['GET', 'POST'])
def register():
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
        if form.sex.data == "male":
            form.sex.data = "Мужской"
        else:
            form.sex.data = "Женский"
        user = User(
            name=form.name.data,
            sex=form.sex.data,
            age=form.age.data,
            email=form.email.data,
            about=form.about.data

        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if not current_user.is_authenticated:
        return redirect("/login")

    themes = db_sess.query(Theme).filter(Theme.user == current_user)

    return render_template("index.html", themes=themes)


@app.route("/themes_by/<int:id>")
def user_themes(id):
    db_sess = db_session.create_session()
    if not current_user.is_authenticated:
        return redirect("/login")

    themes = db_sess.query(Theme).filter(Theme.user_id == id)
    user = db_sess.query(User).filter(User.id == id).first()

    return render_template("user_themes.html", themes=themes, user=user)


@app.route("/profile/<int:id>", methods=["POST", "GET"])
def profile(id):
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        user = db_sess.query(User).filter(User.id == id)[0]
        themes = list(db_sess.query(Theme).filter(Theme.user_id == id))
        return render_template("profile.html", user=user, themes=len(themes))
    return abort(404)


@app.route("/profile_edit/<int:id>", methods=["POST", "GET"])
def profile_edit(id):
    form = ProfileForm()

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id, current_user.id == User.id).first()
    if form.validate_on_submit():
        if user:
            if form.password.data != form.password_again.data:
                return render_template('profile_edit.html',
                                       form=form,
                                       title="Редактирование профиля",
                                       message="Пароли не совпадают")

            if form.sex.data == "male":
                form.sex.data = "Мужской"
            else:
                form.sex.data = "Женский"

            user.set_password(form.password.data)
            user.password = form.password.data
            user.age = form.age.data
            user.sex = form.sex.data
            user.about = form.about.data

            db_sess.commit()
            return redirect(f'/profile/{id}')
        else:
            abort(404)
    if user:
        return render_template('profile_edit.html',
                               form=form,
                               title="Редактирование профиля")
    else:
        abort(404)


@app.route('/themes_add', methods=['GET', 'POST'])
@login_required
def themes_add():
    form = ThemesForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        themes = Theme()
        themes.title = form.title.data
        themes.content = form.content.data
        current_user.themes.append(themes)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('themes_edit.html', title='Добавление темы',
                           form=form)


@app.route('/themes_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def themes_edit(id):
    form = ThemesForm()

    db_sess = db_session.create_session()
    themes = db_sess.query(Theme).filter(Theme.id == id,
                                         Theme.user_id == current_user.id
                                         ).first()
    if form.validate_on_submit():
        if themes:
            themes.title = form.title.data
            themes.content = form.content.data
            db_sess.commit()
            return redirect(f'/themes_get/{id}')
        else:
            abort(404)
    if themes:
        return render_template('themes_edit.html',
                               title='Редактирование темы',
                               form=form
                               )
    else:
        abort(404)


@app.route('/themes_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def themes_delete(id):
    db_sess = db_session.create_session()
    themes = db_sess.query(Theme).filter(Theme.id == id,
                                         Theme.user_id == current_user.id
                                         ).first()
    if themes:
        db_sess.delete(themes)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/themes_get/<int:id>', methods=['GET', 'POST'])
def themes_get(id):
    db_sess = db_session.create_session()
    themes = db_sess.query(Theme).filter(Theme.id == id).first()
    if themes:
        return render_template("themes_get.html", themes=themes)
    else:
        abort(404)
    return redirect('/')


if __name__ == '__main__':
    main()
