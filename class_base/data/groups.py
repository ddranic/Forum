import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Groups(SqlAlchemyBase):
    __tablename__ = 'groups'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    level = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    color = sqlalchemy.Column(sqlalchemy.String)

    group = orm.relation("User", back_populates='groups')

    def __repr__(self):
        return f'<Group> {self.job}'
