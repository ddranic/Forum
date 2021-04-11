from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, RadioField
from wtforms.validators import DataRequired


class ProfileForm(FlaskForm):
    password = PasswordField('Новый пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    age = StringField("Возраст", validators=[DataRequired()])
    sex = RadioField("Пол", choices=[("male", "Мужской"), ("female", "Женский")], validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Изменить данные')
