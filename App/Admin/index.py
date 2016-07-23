
from flask import render_template

from flask_security.decorators import login_required

from App.core import admin_bp
from App.models.public import Series


@admin_bp.route('/index')
@login_required
def index():
    series = Series.query.order_by(Series.order).all()
    return render_template('admin_index.html', series=series)
