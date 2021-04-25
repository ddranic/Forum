from flask import Flask, render_template, redirect, request, abort
from flask_login import login_user, LoginManager, current_user, login_required, logout_user
import locale
from data import db_session
from data.users import User
from data.themes import Theme
from data.comments import Comment
from forms.loginform import LoginForm
from forms.registerform import RegisterForm
from forms.themesform import ThemesForm
from forms.profileform import ProfileForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
locale.setlocale(
    category=locale.LC_ALL,
    locale="ru_RU.utf8"
)

login_manager = LoginManager()
login_manager.init_app(app)

groups = {"offtop": "оффтоп", "computers": "компьютеры",
          "games": "игры", "questions": "вопросы", "ideas": "идеи для форума", "other": "другое"}


def main():
    db_session.global_init("db/blogs.db")

    port = 5000
    app.run(host='127.0.0.1', port=port, debug=True)


@app.errorhandler(404)
def error404(e):
    return render_template("error404.html")


@app.errorhandler(500)
def error505(e):
    return render_template("error404.html")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/")

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
    if current_user.is_authenticated:
        return redirect("/")

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

    themes = db_sess.query(Theme).all()

    return render_template("index.html", themes=themes, sidebar_insist=True)


@app.route("/themes_group/<string:group>")
def themes_group(group):
    db_sess = db_session.create_session()

    if not current_user.is_authenticated:
        return redirect("/login")

    themes = db_sess.query(Theme).filter(Theme.group == group)
    if group in groups:
        group = "в разделе: " + groups[group].capitalize()
    else:
        abort(404)

    return render_template("index.html", themes=themes, sidebar_insist=True, name=group)


@app.route("/themes_by/<int:id>")
def themes_by(id):
    db_sess = db_session.create_session()
    if not current_user.is_authenticated:
        return redirect("/login")

    themes = db_sess.query(Theme).filter(Theme.user_id == id)
    user = db_sess.query(User).filter(User.id == id).first()

    return render_template("index.html", themes=themes, theme_type=user.name, sidebar_insist=True)


@app.route("/profile/<int:id>", methods=["POST", "GET"])
def profile(id):
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        user = db_sess.query(User).filter(User.id == id)[0]
        themes = list(db_sess.query(Theme).filter(Theme.user_id == id))
        return render_template("profile.html", user=user, themes=len(themes), sidebar_insist=True)
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
                                       message="Пароли не совпадают",
                                       sidebar_insist=False)

            if form.sex.data == "male":
                form.sex.data = "Мужской"
            else:
                form.sex.data = "Женский"

            user.set_password(form.password.data)
            user.password = form.password.data
            user.age = form.age.data
            user.sex = form.sex.data
            user.photo = form.photo.data
            user.about = form.about.data

            db_sess.commit()
            return redirect(f'/profile/{id}')
        else:
            abort(404)
    if user:
        return render_template('profile_edit.html',
                               form=form,
                               title="Редактирование профиля",
                               sidebar_insist=False)
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
        themes.group = form.group.data.lower()
        current_user.themes.append(themes)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('themes_add.html', title='Добавление темы',
                           form=form, sidebar_insist=False)


@app.route('/themes_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def themes_delete(id):
    db_sess = db_session.create_session()
    themes = db_sess.query(Theme).filter(Theme.id == id,
                                         Theme.user == current_user
                                         ).first()
    if themes:
        db_sess.delete(themes)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/themes_get/<int:id>', methods=['GET', 'POST'])
def themes_get(id):
    if request.method == "GET":
        db_sess = db_session.create_session()
        theme = db_sess.query(Theme).filter(Theme.id == id).first()
        if theme:
            return render_template("themes_get.html", theme=theme)
        else:
            abort(404)
        return redirect('/')
    elif request.method == "POST":

        content = request.form["comment"]

        db_sess = db_session.create_session()
        theme = db_sess.query(Theme).filter(Theme.id == id).first()
        comment = Comment(content=content, user_id=current_user.id, theme_id=id)

        db_sess.add(comment)
        db_sess.commit()
        return redirect(f"/themes_get/{id}")


if __name__ == '__main__':
    main()
