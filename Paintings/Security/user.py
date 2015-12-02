
from flask import (render_template,
        redirect,
        request,
        url_for,
        session,
        flash,
        current_app)

from .forms import LoginForm
from flask.ext import security
from flask.ext.security.decorators import (login_required, anonymous_user_required)
from flask.ext.security.utils import (login_user, logout_user)
from flask_login import current_user

from ..core import admin_bp 


@admin_bp.route('/login', methods=['GET', 'POST'])
@anonymous_user_required
def login():
    form = LoginForm()

    if form.validate_on_submit():
        login_user(form.user)
        session['auth_username'] = form.user.username

        return redirect(url_for('Admin.index'))
    else:
        if form.is_submitted():
            return redirect(url_for('.login'))

    return render_template('security/login_user.html', form=form)


@admin_bp.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated():
        current_app.logger.info('logged out')
        logout_user()
        # session.clear()
        # change redirect to public.index
        return 'you have been logged out<br><a href="{}">index</a>'.format(url_for('.login'))
    else:
        # session.clear()
        return '<h1>you are not logged in</h1>'

# @admin_bp.route('/userproperties')
def user_properties():
    return 'change password || admin email'

