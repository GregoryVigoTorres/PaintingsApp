from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import relationship 
from flask.ext.security import UserMixin, RoleMixin
from flask.ext.security import SQLAlchemyUserDatastore

import uuid
import datetime

from ..core import db


roles_users = db.Table('roles_users', 
        db.Column('user_id', UUIDType(binary=False), db.ForeignKey('user.id')),
        db.Column('role_id', UUIDType(binary=False), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column('id', UUIDType(binary=False), primary_key=True, default=str(uuid.uuid4()))
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column('id', UUIDType(binary=False), primary_key=True, default=str(uuid.uuid4()))
    email = db.Column('email', db.String(length=255), nullable=False)
    password = db.Column('password', db.String(length=255), nullable=False)
    active = db.Column(db.Boolean())

    username = db.Column('username', db.String(length=255), nullable=False)
    date_created = db.Column('date_created', db.DateTime(), default=datetime.datetime.now())
    last_login = db.Column('last_login', db.DateTime(), default=datetime.datetime.now())
    current_login_at = db.Column('current_login_at', db.DateTime(), default=datetime.datetime.now())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic')) 
    

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
