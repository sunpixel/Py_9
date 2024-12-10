'''Module that will populate the DB with default data set'''

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Text, ForeignKey

from Main.base_class import Base

class User(Base):
    '''A class representing a table in the DB'''
    __tablename__ = 'Users'

    id =        Column(Integer, primary_key=True, index=True, unique=True)
    username =  Column(String, unique=True)
    email =     Column(String, unique=True)
    password =  Column(String)

    posts = relationship('Post', back_populates='users')

class Post(Base):
    '''A class that represents table in DB'''
    __tablename__ = 'Posts'

    id =        Column(Integer, primary_key=True, index=True, unique=True)
    title =     Column(String)
    content =   Column(Text)
    user_id =   Column(Integer, ForeignKey('Users.id'))

    users = relationship('User', back_populates='posts')
