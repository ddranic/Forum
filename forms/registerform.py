from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, RadioField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    age = StringField("Возраст", validators=[DataRequired()])
    sex = RadioField("Пол", choices=[("male", "Мужской"), ("female", "Женский")], validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Создать аккаунт')
