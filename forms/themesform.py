from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired, length


class ThemesForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired(), length(max=70)])
    content = TextAreaField("Содержание")
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')