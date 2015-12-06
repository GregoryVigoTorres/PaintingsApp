"""
Create and delete users and (eventually) change user passwords
"""

from flask.ext.script import (Command, prompt, prompt_pass)
from flask.ext.security.utils import encrypt_password
from flask import current_app
from sqlalchemy import or_

from wtforms.validators import ValidationError
from App.lib.validators import (strong_password, valid_email)
from ..models.user import User, user_datastore
from ..core import db


class CreateUser(Command):
    """ Not currently doing anything with roles
    """
    def run(self):
        """ flask-security requires email and password fields 
        """
        
        db_conf = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        if not db_conf:
            print('DB URI not found')
            return None

        db_uri = db_conf.split('/')[-1]
        print('>connected to db: {}'.format(db_uri))

        username = prompt('>username')
        user_exists = User.query.filter_by(username=username).first()
        
        if user_exists is not None:
            raise ValidationError('>>a user with that username already exists')
            return None

        _email = prompt('>email')

        try:
            valid_email(_email)
        except ValidationError as e:
            print(e)
            return None

        password = prompt_pass('>password')
        password2 = prompt_pass('>password again')

        if password != password2:
            raise ValidationError('>>the passwords are not the same')
        else:            
            try:
                strong_password(password)
                password = encrypt_password(password)
                user_datastore.create_user(username=username, 
                        password=password, 
                        email=_email)
                db.session.commit()
                print('>added user: {}'.format(username))

            except ValidationError as e:
                print('>>{}'.format(e))

class DeleteUser(Command):
    """ find user by username or email
    there's no going back after user is deleted"""
    def run(self):
        id_token = prompt('>enter username or email of user to delete')
        _user = User.query.filter(or_(User.username == id_token, User.email == id_token)).first()
        if _user:
            user_datastore.delete_user(_user)
            db.session.commit()
            print('{} has been permanently deleted'.format(_user.username))
        else:
            print('{} does not exist'.format(id_token))

