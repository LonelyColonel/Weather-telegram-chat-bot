import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):

    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    telegram_id = sqlalchemy.Column(sqlalchemy.BIGINT)
    city = sqlalchemy.Column(sqlalchemy.VARCHAR(30))
    lon = sqlalchemy.Column(sqlalchemy.VARCHAR(15))
    lat = sqlalchemy.Column(sqlalchemy.VARCHAR(15))
    date_create = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f'{str(self.id)}={str(self.telegram_id)}={str(self.city)}={str(self.lon)}={str(self.lat)}=' \
               f'{str(self.date_create)}'

    # def __repr__(self):
    #     return [self.id, self.telegram_id, self.city, self.lon, self.lat, self.date_create]
