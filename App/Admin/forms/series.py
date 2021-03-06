
import uuid
import datetime
from wtforms import (HiddenField,
                    StringField,
                    DateTimeField,
                    )

from flask_wtf import Form
from wtforms.validators import (DataRequired,
                                InputRequired,
                                )

from App.lib.validators import valid_uuid

class SeriesForm(Form):
    id = HiddenField('series_id', default=uuid.uuid4(), validators=[valid_uuid(), DataRequired()])
    auth_token = HiddenField('auth_token') # can't use current app outside context
    title = StringField(label='title', validators=[InputRequired()])#, widget=richTextInput)
    order = HiddenField()
    date_created = DateTimeField(default=datetime.datetime.utcnow())
