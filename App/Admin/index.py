
from flask import render_template

from flask.ext.security.decorators import login_required

from ..core import admin_bp
from ..models.public import Series


@admin_bp.route('/index')
@login_required
def index():
    series = Series.query.order_by(Series.order).all()
    return render_template('admin_index.html', series=series)
