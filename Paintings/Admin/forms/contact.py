import uuid
import datetime
import re

from flask import (current_app, flash)

from flask.ext.wtf import Form
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

from Paintings.lib.validators import UUIDType


def no_html(form, field):
    """
        field data cannot contain any html tags
        escaping is handled by jinja
    """
    tag_re = re.compile('(<[a-zA-Z ]+>*)(</)*')
    has_tags = re.search(tag_re, field.data)
    if has_tags:
        raise ValidationError(message='html tags are not allowed')

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
    id = HiddenField('image_id', default=uuid.uuid4(), validators=[UUIDType(), DataRequired(message='required')])
    date_created = DateTimeField(default=datetime.datetime.now())
    name = StringField(label='name',  validators=[no_html, dependent_fields, Optional(), Length(max=255)])
    url = StringField(label='full url',    validators=[no_html, dependent_fields, Optional(), URL()])
    email= StringField(label='email', validators=[no_html, dependent_fields, Optional(), Email()])
    icon = FileField(label='icon')
