import uuid
import datetime
import re

import colour

from flask import (current_app, flash)

from flask_wtf import Form
from flask_wtf.file import (FileField, FileAllowed)
from wtforms import (TextField,
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

from App.lib.validators import (valid_color, valid_uuid, exor)
from App.lib.form_fields import HexColorField


class ImageForm(Form):
    id = HiddenField('image_id',
                     default=uuid.uuid4(),
                     validators=[valid_uuid(),
                     DataRequired(message='required')])
    title = StringField(label='title', validators=[DataRequired(message='required')])
    auth_token = HiddenField('auth_token')
    medium = StringField(label='medium', default="Acrylic on paper")
    date_created = DateTimeField()
    date = IntegerField('date', validators=[
        NumberRange(min=1975,
                    max=2025,
                    message='must be year like 20YY')
    ])

    filename = HiddenField('filename')
    image = FileField('image_file',
                      validators=[DataRequired(message='you must upload a file'),
                                                FileAllowed(['jpg', 'jpeg', 'png'],
                                                'image must be a jpeg or png file')])

    dimensions = FieldList(IntegerField('dimensions',
                                        validators=[
                                            NumberRange(min=1, max=5000, message='must be between %(min)s and %(max)s')
                                            ]),
                                        min_entries=2,
                                        max_entries=2,
                                        default=[0,0],
                                        )

    padding_color = HexColorField('padding color', validators=[valid_color])
    series_id = HiddenField('series_id', validators=[valid_uuid(), DataRequired(message='required')])
    medium_id = HiddenField('medium_id', validators=[Optional(), valid_uuid()])


class BulkImageForm(Form):
    auth_token = HiddenField('auth_token')
    medium = StringField(label='medium', default="Acrylic on paper")
    date_created = DateTimeField()
    title_re_to = StringField(label='title regex to')
    title_re_from = StringField(label='title regex from')
    date_re = StringField(label='date regex', validators=[exor('date_str')])
    date_str = IntegerField('date string',
                            validators=[
                                Optional(),
                                NumberRange(min=1975,
                                            max=2025,
                                            message='must be year like 20YY')
                            ])
    images = FileField('image_files',
                               validators=[DataRequired(message='you must choose at least one file'),
                                                FileAllowed(['jpg', 'jpeg', 'png', 'gif'],
                                                'files must all be images')])

    dimensions = FieldList(IntegerField('dimensions',
                                        validators=[
                                            NumberRange(min=1, max=5000, message='must be between %(min)s and %(max)s')
                                            ]),
                                        min_entries=2,
                                        max_entries=2,
                                        default=[21,27],
                                        )

    padding_color = HexColorField('padding color', validators=[valid_color])
    series_id = HiddenField('series_id', validators=[valid_uuid(), DataRequired(message='required')])


class EditImageForm(ImageForm):
    """ Images that are already in the database already have a file.
        This subclass allows the image file to be optional.
    """
    # this field is required for NEW IMAGES
    image = FileField('image_file', validators=[Optional(),
                                                FileAllowed(['jpg', 'jpeg', 'png'],
                                                'image must be a jpeg or png file')]
                                                )
