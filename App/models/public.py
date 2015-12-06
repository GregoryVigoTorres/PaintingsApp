import uuid
import datetime

from sqlalchemy_utils import (UUIDType, ColorType)
from sqlalchemy.orm import relationship 
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.schema import Sequence

from ..core import db


class Series(db.Model):
    __tablename__ = 'series'

    id = db.Column('id', UUIDType(binary=False), primary_key=True, default=str(uuid.uuid4()))
    title = db.Column('title', db.String(length=255), nullable=False)
    date_created = db.Column('date_created', db.DateTime(), default=datetime.datetime.now)
    order = db.Column('order', db.Integer(), nullable=False) 
    
    images = db.relationship('Image',
            backref='series',
            cascade='all, delete, delete-orphan',
            lazy='joined',
            order_by='Image.order')

    def __repr__(self):
        return '<{}>'.format(self.title)


class Medium(db.Model):
    __tablename__ = 'medium'
    
    id = db.Column('id', UUIDType(binary=False), primary_key=True, default=str(uuid.uuid4()))
    name = db.Column('name', db.String(length=255), nullable=False, unique=True)

    images = db.relationship('Image',
            backref='medium',
            cascade='save-update',
            lazy='joined')
            
    def __repr__(self):
        return self.name


class Image(db.Model):
    __tablename__ = 'images'
    
    id = db.Column('id', UUIDType(binary=False), primary_key=True, default=str(uuid.uuid4()))
    title = db.Column('title', db.String(length=255), nullable=False)
    date_created = db.Column('date_created', db.DateTime(), default=datetime.datetime.now)
    medium_id = db.Column('medium_id', UUIDType(binary=False), db.ForeignKey('medium.id'), nullable=True)
    img_ord_seq = Sequence('img_ord_seq')
    order = db.Column('order', 
            db.Integer, img_ord_seq, 
            server_default=img_ord_seq.next_value(), 
            nullable=True) 
    
    date = db.Column('date', db.Integer()) # year as XXXX
    filename = db.Column('filename', db.String(), nullable=False)
    dimensions = db.Column('dimensions', ARRAY(db.Integer, dimensions=1))
    padding_color = db.Column('padding_color', ColorType())
    series_id = db.Column('series_id', UUIDType(binary=False), db.ForeignKey('series.id'), nullable=False)

    def __repr__(self):
        return '<{}>'.format(self.title)

class Text(db.Model):
    __tablename__ = 'texts'
    id = db.Column('id', UUIDType(binary=False), primary_key=True, default=str(uuid.uuid4()))
    date_created = db.Column('date_created', db.DateTime(), default=datetime.datetime.now)
    date = db.Column('date', db.Integer(), nullable=True) # year as XXXX
    title = db.Column('title', db.String(length=255), nullable=False)
    author = db.Column('author', db.String(length=255), nullable=True)
    body = db.Column('body', db.Text(), nullable=False)

    def __repr__(self):
        return '<{}>'.format(self.title)

class Link(db.Model):
    __tablename__ = 'links'
    id = db.Column('id', UUIDType(binary=False), primary_key=True, default=str(uuid.uuid4()))
    date_created = db.Column('date_created', db.DateTime(), default=datetime.datetime.now)
    label = db.Column('label', db.String(length=255), nullable=False)
    link_target = db.Column('link_target', db.String(), nullable=False)
    description = db.Column('description', db.Text(), nullable=True)

    def __repr__(self):
        return '<{}>'.format(self.label)

class Contact(db.Model):
    __tablename__ = 'contact_info'
    id = db.Column('id', UUIDType(binary=False), primary_key=True, default=str(uuid.uuid4()))
    date_created = db.Column('date_created', db.DateTime(), default=datetime.datetime.now)
    name = db.Column('name', db.String(length=255), nullable=True)
    url = db.Column('url', db.String(), nullable=True)
    email = db.Column('email', db.String(), nullable=True)
    icon_filename = db.Column('icon_filename', db.String(length=255), nullable=True)

    def __repr__(self):
        if self.name:
            name = self.name
        if self.email:
            name = self.email

        return '<{}>'.format(name)



