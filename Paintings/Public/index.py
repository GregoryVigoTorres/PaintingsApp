from flask import render_template

from ..core import (db, public_bp)
from ..models.public import Series

@public_bp.route('/')
@public_bp.route('/index')
@public_bp.route('/index/<_id>')
def index(_id=None):
    # needs limit for no. of images
    if _id:
        series = Series.query.get(_id)
    else:
        series = db.session.query(Series).order_by(Series.order).first()
    return render_template('public_index.html', series=series)

