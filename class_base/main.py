from flask import Flask, render_template, redirect, request, abort
from forms.loginform import LoginForm
from data.users import User
from forms.registerform import RegisterForm
from data import db_session
from data.themes import Theme
from forms.themesform import ThemesForm
from flask_login import login_user, LoginManager, current_user, login_required, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/blogs.db")
    app.run()


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


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        themes = db_sess.query(Theme).filter(
            (Theme.user == current_user) | (Theme.is_private != True))
    else:
        themes = db_sess.query(Theme).filter(Theme.is_private != True)
    return render_template("index.html", themes=themes)


@app.route('/themes', methods=['GET', 'POST'])
@login_required
def add_news():
    form = ThemesForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        themes = Theme()
        themes.title = form.title.data
        themes.content = form.content.data
        themes.is_private = form.is_private.data
        current_user.themes.append(themes)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('themes.html', title='Добавление темы',
                           form=form)


@app.route('/themes/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_themes(id):
    form = ThemesForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        themes = db_sess.query(ThemesForm).filter(Theme.id == id,
                                                  Theme.user == current_user
                                                  ).first()
        if themes:
            form.title.data = themes.title
            form.content.data = themes.content
            form.is_private.data = themes.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        themes = db_sess.query(Theme).filter(Theme.id == id,
                                             Theme.user == current_user
                                             ).first()
        if themes:
            themes.title = form.title.data
            themes.content = form.content.data
            themes.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('themes.html',
                           title='Редактирование темы',
                           form=form
                           )


@app.route('/themes_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def themes_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(Theme).filter(Theme.id == id,
                                       Theme.user == current_user
                                       ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


if __name__ == '__main__':
    main()
