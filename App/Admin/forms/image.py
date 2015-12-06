
import uuid
import datetime
import re

import colour

from flask import (current_app, flash)

from flask.ext.wtf import Form
from flask_wtf.file import (FileField, FileAllowed)
from wtforms_components import ColorField
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

from App.lib.validators import UUIDType

class HexColorField(ColorField):
    """
    subclassed to return actually usable color value
    """

    def _value(self):
        """
        I think default_value can also be an HTML color name
        """
        self.default_value = '#000000'
        
        if isinstance(self.data, colour.Color):
            return self.data.get_hex_l()
        else:
            col = colour.Color(self.default_value)
            return col.get_hex_l()


def ValidColor(form, field):
    """
    raise ValidationError or return None
    """
    if isinstance(field.data, colour.Color) is False:
        raise ValidationError('Invalid color')

    as_hex = field.data.get_hex_l()
    valid_hex = re.match('#[a-zA-Z0-9]{6}', as_hex)

    if valid_hex is None:
        raise ValidationError('{} is not a valid color value'.format(as_hex))

class ImageForm(Form):
    id = HiddenField('image_id', default=uuid.uuid4(), validators=[UUIDType(), DataRequired(message='required')])
    title = StringField(label='title', validators=[DataRequired(message='required')])
    auth_token = HiddenField('auth_token')
    medium = StringField(label='medium', default="Acrylic on paper")
    date_created = DateTimeField()
    date = IntegerField('date', validators=[NumberRange(min=1975, max=2025, message='must be year like 20YY')]) 

    filename = HiddenField('filename')
    image = FileField('image_file', validators=[DataRequired(message='you must upload a file'),
                                                FileAllowed(['jpg', 'jpeg', 'png'], 
                                                'image must be a jpeg or png file')])

    dimensions = FieldList(IntegerField('dimensions', 
                                        validators=[
                                            NumberRange(min=1, max=500, message='must be between %(min)s and %(max)s')
                                            ]),
                                        min_entries=2, 
                                        max_entries=2, 
                                        default=[0,0],
                                        )

    padding_color = HexColorField('padding color', validators=[ValidColor]) 
    series_id = HiddenField('series_id', validators=[UUIDType(), DataRequired(message='required')])
    medium_id = HiddenField('medium_id', validators=[Optional(), UUIDType()])

class EditImageForm(ImageForm):
    """ Images that are already in the database already have a file.
        This subclass allows the image file to be optional.
    """
    # this field is required for NEW IMAGES
    image = FileField('image_file', validators=[Optional(),
                                                FileAllowed(['jpg', 'jpeg', 'png'], 
                                                'image must be a jpeg or png file')]
                                                )
