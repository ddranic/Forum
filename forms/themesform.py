from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired, length


class ThemesForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), length(max=70)])
    content = TextAreaField("Содержание", validators=[DataRequired()])
    group = RadioField("Тематика", choices=[("Offtop", "Оффтоп"),
                                            ("Computers", "Компьютеры"),
                                            ("Games", "Игры"),
                                            ("Questions", "Вопросы"),
                                            ("Ideas", "Идеи для форума"),
                                            ("Other", "Другое")],
                       validators=[DataRequired()])
    submit = SubmitField('Применить')
