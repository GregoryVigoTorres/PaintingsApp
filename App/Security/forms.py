
import uuid
import datetime
import re

from flask import (current_app, flash, session)

from flask.ext.security.utils import (get_message, verify_and_update_password)

from flask.ext.wtf import Form
from wtforms import (HiddenField, 
                    StringField, 
                    PasswordField
                    )

from wtforms.validators import (DataRequired,
                                NumberRange,
                                UUID,
                                Required,
                                InputRequired,
                                ValidationError,
                                Length,
                                URL,
                                Email,
                                Optional,
                                )

from ..models.user import User


class LoginForm(Form):
    """ override default login form """

    username = StringField()
    password = PasswordField()

    def validate(self):
        """ this is a slimmed down version of the default validate function
        where username is used instead of email for user authentication
        """

        if self.password.data.strip() == '':
            flash('password required')
            return False

        if self.username.data.strip() == '':
            flash('username required')
            return False

        self.user = User.query.filter_by(username=self.username.data).first()

        if not self.user:
            flash('invalid username')
            current_app.logger.warning('invalid login attempt by {}'.format(self.username.data))
            return False

        if not verify_and_update_password(self.password.data, self.user):
            current_app.logger.warning('invalid password')
            flash('invalid password')
            return False

        return True
