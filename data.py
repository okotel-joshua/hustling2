import enum
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from flask_login import UserMixin
from hashlib import md5
from flask_admin import Admin


Base = declarative_base()
#admin= Admin(app)

class Users(UserMixin, Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False, unique=True, index=True)
    email = Column(String(250), unique=True, index=True)
    password = Column(String(250))



    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'email': self.email,
            'password': self.password,
            'id': self.id,
        }


        # def is_anonymous(self):
        # return False

        # def get_id(self):
        # return self.id

        # def __repr__(self):
        # return '<User %r>' % (self.name)
class User():
    def __init__(self, email):
        self.email = email

    def get_id(self):
        return self.email

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)


class MyEnum(enum.Enum):
    Private = 1
    Public = 2


class Events(Base):
    __tablename__ = 'events'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    category = Column(String(250))
    fee = Column(String(8))
    date = Column(Date)
    time = Column(Time)
    location = Column(String(250))
    organisers = Column(String(250))
    description = Column(String(250))
    category = Column(Enum('Fellowship','Festivals','Birthday','Shows','Concerts','Sports','Others'))
    privacy = Column(Enum(MyEnum))
    pictures = Column(String(250))
    register_id = Column(Integer, ForeignKey('users.id'))
    users = relationship(Users)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'date': self.date,
            'time': self.time,
            'location': self.location,
            'organisers': self.organisers,
            'description': self.description,
            'category': self.category,
            'id': self.id,
        }
#
# admin.add_view(ModelView(Users))
# admin.add_view(ModelView(Events))


engine = create_engine('sqlite:///handler.db')

Base.metadata.create_all(engine)
