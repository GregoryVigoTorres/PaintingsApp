import uuid
import datetime
import re

from flask import (current_app, flash)

from flask_wtf import Form
from flask_wtf.file import (FileField, FileAllowed)
from wtforms import (TextAreaField,
                    HiddenField,
                    StringField,
                    DateTimeField,
                    IntegerField,
                    FieldList,
                    )

from wtforms.validators import (DataRequired,
                                NumberRange,
                                Required,
                                InputRequired,
                                ValidationError,
                                Length,
                                URL,
                                Email,
                                Optional,
                                )

from App.lib.validators import (valid_uuid, no_html)


def dependent_fields(form, field):
    """name is required if url has data,
        email cannot have data
    """
    if not form.name.data and not form.url.data and not form.email.data:
        raise ValidationError(message='input required')

    if form.email.data:
        # name and url can be empty
        return True

    if not form.name.data and not form.url.data:
        raise ValidationError(message='links must have a name and url')


class ContactForm(Form):
    auth_token = HiddenField('auth_token')
    id = HiddenField('image_id', default=uuid.uuid4(), validators=[valid_uuid(), DataRequired(message='required')])
    date_created = DateTimeField(default=datetime.datetime.now())
    name = StringField(label='name',  validators=[no_html, dependent_fields, Optional(), Length(max=255)])
    url = StringField(label='full url',    validators=[no_html, dependent_fields, Optional(), URL()])
    email= StringField(label='email', validators=[no_html, dependent_fields, Optional(), Email()])
    icon = FileField(label='icon')
