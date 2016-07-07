from flask import current_app
from flask_security.core import current_user

from App.models.public import Series
from App.core import db

def get_all_series():
    """ template global 
    """
    all_series = db.session.query(Series.title, Series.id).order_by(Series.order).all()
    return all_series


def get_auth_token():
    """ make current_user auth token available in templates """
    __name__ = 'get_auth_token'
    with current_app.app_context():
        if current_user and current_user.is_authenticated:
            return current_user.get_auth_token()

