import datetime
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True, unique=True)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    sex = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    speciality = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    group = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("groups.id"))
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    about = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    photo = sqlalchemy.Column(sqlalchemy.String, default="https://cdn0.iconfinder.com/data/icons/set-ui-app-android/32/8-512.png")
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    votes = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    groups = orm.relation("Groups")
    themes = orm.relation("Theme", back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
