import os.path
import re
import uuid

from flask import (current_app,
                   flash,
                   redirect,
                   render_template,
                   request,
                   url_for)
from flask.views import MethodView
from flask_security.decorators import login_required

from werkzeug.exceptions import NotFound

from App.core import db
from App.lib.utils import flash_form_errors
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
        self.tmpl_args['series'] = series
        return series

    def get_meta_attrs(self):
        meta_attrs = {'series': self.series,
                      'series_id': self.series.id}

        for k, v in self.form.data.items():
            if hasattr(Image, k):
                meta_attrs[k] = v

        return meta_attrs

    def get_medium(self):
        if self.meta_attrs.get('medium'):
            medium = Medium.query.filter_by(
                name=self.meta_attrs['medium']
            ).first()

            if not medium:
                medium = Medium(name=self.meta_attrs['medium'])
            return medium

    def update_title_regex(self):
        """
        Override default title parsing regexes
        with submitted form data
        """
        self.title_re_to = request.form.get('title_re_to') \
            or self.title_re_to
        self.title_re_from = request.form.get('title_re_from') \
            or self.title_re_from

        self.title_re_from = re.compile(self.title_re_from)

    def get_image_meta(self):
        """
        get meta_attrs and update regexes
        that are needed for saving all images
        """
        self.meta_attrs = self.get_meta_attrs()
        medium = self.get_medium()
        if medium:
            self.meta_attrs['medium'] = medium

        self.update_title_regex()

    def get_title(self, orig_filename):
        title = re.sub(self.title_re_from, self.title_re_to, orig_filename)
        return title

    def get_date(self, request, orig_filename):
        """
        either parse date from date_re or
        use provided string
        """
        date_re = request.form.get('date_re')
        date_str = request.form.get('date_str')

        if date_re:
            date = re.sub(self.title_re_from, date_re, orig_filename)
            return date

        if date_str:
            return date_str

    def get_image_object(self, img_attrs):
        image = Image()
        image.id = uuid.uuid4()

        for k, v in img_attrs.items():
            if hasattr(image, k):
                setattr(image, k, v)

        return image

    def process_image(self, img):
        """
        save images to disk and in the database
        """
        orig_filename = os.path.splitext(os.path.basename(img.filename))[0]

        if not re.search(self.title_re_from, orig_filename):
            return None

        title = self.get_title(orig_filename)
        date = self.get_date(request, orig_filename)

        img_attrs = {'title': title,
                     'date': date}

        img_attrs.update(self.meta_attrs)

        # save to disk
        filename = save_image(img)
        img_attrs['filename'] = filename

        if not filename:
            return None

        image = self.get_image_object(img_attrs)

        return image

    def write_images(self, images):
        """
        write images to database
        """
        db.session.add_all(images)

        try:
            db.session.commit()
            return True
        except Exception as E:
            print(E)
            current_app.logger.info('Could not save images')

    def post(self, series_id):
        self.series = self.get_series(series_id)
        if not self.series:
            raise NotFound

        if self.form.validate_on_submit():
            self.get_image_meta()

            images = [self.process_image(i)
                      for i in request.files.getlist('images')]

            save_images = [i for i in images if i]
            image_errors = [i for i in images if not i]
            # write images to db
            images_written = self.write_images(save_images)

            message = ''
            if images_written:
                message = '{} images added to {}. '.format(
                    len(save_images), self.series.title
                )
            else:
                message = 'There was a problem saving the images'

            if len(image_errors):
                message += '{} images could not be saved'.format(
                    len(image_errors)
                )

            current_app.logger.info(message)
            flash(message)

        if len(self.form.errors) > 0:
            flash_form_errors(self.form.errors)

        return redirect(url_for('Admin.bulk_upload', series_id=series_id))

    def get(self, series_id):
        series = self.get_series(series_id)
        if not series:
            raise NotFound

        return render_template('admin_upload_images.html', **self.tmpl_args)
