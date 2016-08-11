from flask import (current_app,
                   redirect,
                   render_template,
                   request,
                   url_for)
from flask.views import MethodView
from flask_security.decorators import login_required

from werkzeug.exceptions import NotFound

from App.models.public import Series, Image, Medium

from .forms.image import BulkImageForm
from .utils import save_image


class BulkUpload(MethodView):
    decorators = [login_required]
    def __init__(self,):

        self.form = BulkImageForm()
        self.title_re_to = current_app.config.get('DEFAULT_TITLE_RE_TO')
        self.title_re_from = current_app.config.get('DEFAULT_TITLE_RE_FROM')
        self.date_re = current_app.config.get('DEFAULT_DATE_REGEX')

        self.tmpl_args = {'form': self.form,
                          'title_re_to': self.title_re_to,
                          'title_re_from': self.title_re_from,
                          'date_re': self.date_re}

    def get_series(self, series_id):
        series_id = series_id
        series = Series.query.get(series_id)
        return series

    def get(self, series_id):
        series = self.get_series(series_id)
        if not series:
            raise NotFound
        self.tmpl_args['series'] = series

        return render_template('admin_upload_images.html', **self.tmpl_args)


    def post(self, series_id):
        series = self.get_series(series_id)
        if not series:
            raise NotFound
        self.tmpl_args['series'] = series

        return redirect(url_for('Admin.bulk_upload', series_id=series_id))
