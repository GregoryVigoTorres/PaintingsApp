import itertools
from flask import flash

from App.models.public import Series
from App.core import db

def flash_form_errors(errors):
    flash('<p>Oops!</p>')
    for k, msg in errors.items():
        if isinstance(msg, list):
            # sometimes messages are a nested list, 
            # and sometimes they're not
            if isinstance(msg[0], list):
                msg = itertools.chain.from_iterable(msg)
            msg = ', '.join(set(msg))
            key = k.replace('_', ' ').title()
        flash('<strong>{}... </strong> {}'.format(key, msg))

def get_all_series():
    """ template global 
    """
    all_series = db.session.query(Series.title, Series.id).order_by(Series.order).all()
    return all_series

