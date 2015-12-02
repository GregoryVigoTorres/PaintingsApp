

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
    tag_re = re.compile('<*>')
    has_tags = re.search(tag_re, field.data)
    if has_tags:
        raise ValidationError(message='html tags are not allowed')

class TextLinkFormBase(Form):
    auth_token = HiddenField('auth_token')
    id = HiddenField('image_id', default=uuid.uuid4(), validators=[UUIDType(), DataRequired(message='required')])
    date_created = DateTimeField(default=datetime.datetime.now())
    date = IntegerField('date', validators=[Optional(), NumberRange(min=1975, max=2025, message='must be year like 20YY')]) 

class TextForm(TextLinkFormBase):
    title = StringField(label='*title', validators=[DataRequired(message='required'), no_html, Length(max=255)])
    author = StringField(label='*author', validators=[DataRequired(message='required'), no_html, Length(max=255)])
    body = TextAreaField(label='text body', validators=[DataRequired(message='required'), no_html, Length(max=3000)])
    uploaded_file = FileField('uploaded_file', )

class LinkForm(TextLinkFormBase):
    label = StringField(label='*label', validators=[DataRequired(message='required'), Length(max=255), no_html])
    link_target = StringField(label='*link url', validators=[no_html, Optional(), URL()])
    description = TextAreaField(label='link description', validators=[Optional(), no_html, Length(max=1000)])
