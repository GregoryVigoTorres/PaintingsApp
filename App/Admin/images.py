from pathlib import Path
import re
import sys
import uuid

from flask import (render_template,
                   redirect,
                   request,
                   url_for,
                   flash,
                   jsonify,
                   current_app)

from flask_security.decorators import (login_required, auth_token_required)

from werkzeug.exceptions import NotFound

from .forms.image import (ImageForm, EditImageForm, BulkImageForm)
from .utils import (save_image,
                    upsert_image_from_form,
                    parse_bulk_upload_filename)

from App.lib.utils import flash_form_errors
from App.core import (db, admin_bp)
from App.models.public import Series, Image, Medium
from .bulk_upload import BulkUpload


admin_bp.add_url_rule('/uploadimages/<series_id>', view_func=BulkUpload.as_view('bulk_upload'))


@admin_bp.route('/newimage/<series_id>', methods=['GET', 'POST'])
@login_required
def new_image(series_id):
    """ images can only be added to an existing series
        series_id is passed in the url and the form data
        TODO:
        choose other series
    """
    try:
        series = Series.query.filter_by(id=series_id).first()
        assert series
    except:
        raise NotFound()

    form = ImageForm()
    tmpl_args = {
        'page_title': 'add a new image to &ldquo;{}&rdquo;'.
        format(series.title)
    }

    # this fixes a bug where the same id is
    # getting used more than once in the image form
    form.id.data = uuid.uuid4()

    if form.validate_on_submit():
        image = upsert_image_from_form(form)
        filename = save_image(request.files['image'])

        if filename:
            image.filename = filename
            db.session.commit()
            flash('{} <br>added to {}'.format(image.title, image.series.title))
            msg = '[{}] added to [{}]'.format(image.title, image.series.title)
            current_app.logger.info(msg)

        else:
            flash('There was a problem saving the image')

        return redirect(url_for('Admin.edit_image', image_id=image.id))

    if len(form.errors) > 0:
        flash_form_errors(form.errors)
        return redirect(url_for('Admin.new_image', series_id=series_id))

    return render_template('admin_image.html',
                           form=form, series=series,
                           **tmpl_args)


# @admin_bp.route('/uploadimages/<series_id>', methods=['GET', 'POST'])
# @login_required
def bulk_upload(series_id):
    """
    Upload a lot of images to a series at once
    according to criteria applied to all the files

    ToDo:
        break this out into separate functions
        OR a class based view
        make it possible to use user entered date instead of
        always using DEFAULT_DATE_RE
    """
    series = Series.query.get(series_id)

    if not series:
        raise NotFound

    form = BulkImageForm()

    title_re_to = current_app.config.get('DEFAULT_TITLE_RE_TO')
    title_re_from = current_app.config.get('DEFAULT_TITLE_RE_FROM')
    date_re = current_app.config.get('DEFAULT_DATE_REGEX')

    tmpl_args = {'series': series,
                 'form': form,
                 'title_re_to': title_re_to,
                 'title_re_from': title_re_from,
                 'date_re': date_re}

    # request POST
    if len(form.errors) > 0:
        flash_form_errors(form.errors)

    if form.validate_on_submit():
        # get dict of values for all images
        meta_attrs = {'series': series,
                      'series_id': series.id}

        for k, v in form.data.items():
            if hasattr(Image, k):
                meta_attrs[k] = v

        # get medium object
        if meta_attrs.get('medium'):
            medium = Medium.query.filter_by(name=meta_attrs['medium']).first()
            if not medium:
                medium = Medium(name=meta_attrs['medium'])
            # meta_attrs['medium_id'] = medium.id
            meta_attrs['medium'] = medium
        else:
            meta_attrs.pop('medium')

        # Get re.sub patterns from form
        title_re_to = request.form.get('title_re_to') or title_re_to
        title_re_from = request.form.get('title_re_from') or title_re_from
        date_re = request.form.get('date_re') or date_re

        title_re_from = re.compile(title_re_from)

        # process each file
        count = 0
        error_count = 0
        images = []

        for img in request.files.getlist('images'):
            # this for loop is (still) too long
            img_attrs = {}
            img_attrs.update(meta_attrs)

            title, date = parse_bulk_upload_filename(img,
                                                     title_re_from,
                                                     title_re_to,
                                                     date_re)

            if title is None or date is None:
                error_count += 1
                continue

            img_attrs['title'] = title
            img_attrs['date'] = date

            # save_image (to disk) if it has a valid title and date
            filename = save_image(img)
            if not filename:
                error_count += 1
                continue

            img_attrs['filename'] = filename

            # Save to database
            # Don't update existing images
            image = Image()
            image.id = uuid.uuid4()

            for k, v in img_attrs.items():
                if hasattr(image, k):
                    setattr(image, k, v)

            images.append(image)
            count += 1

        db.session.add_all(images)
        db.session.commit()

        flash("""{} images uploaded to {} and {} not uploaded.
              <br>You may want to update the image order""".format(
            count, series.title, error_count)
        )
        return redirect(url_for('Admin.bulk_upload', series_id=series_id))

    return render_template('admin_upload_images.html', **tmpl_args)


@admin_bp.route('/editimage/<image_id>', methods=['GET', 'POST'])
@login_required
def edit_image(image_id):
    try:
        image = Image.query.filter_by(id=image_id).first()
    except:
        raise NotFound()

    if not image:
        raise NotFound()

    series = image.series

    tmpl_args = {
        'page_title': """
        editing &ldquo;{}&rdquo; in &ldquo;{}&rdquo;
        """.format(image.title, series.title)
    }
    form = EditImageForm(obj=image)

    if form.validate_on_submit():
        image = upsert_image_from_form(form)
        image_file = request.files.get('image')

        if image_file:
            filename = save_image(request.files['image'])
            if filename:
                image.filename = filename
            else:
                flash('There was a problem saving the image')

        db.session.commit()
        flash('&ldquo;{}&rdquo; has been changed'.format(image.title))
        msg = 'Image [{}] in [{}] modified'.format(image.title, series.title)
        current_app.logger.info(msg)

        return redirect(url_for('Admin.edit_image', image_id=image.id))

    if len(form.errors) > 0:
        flash_form_errors(form.errors)
        return redirect(url_for('Admin.edit_image', image_id=image.id))
    return render_template('admin_image.html',
                           form=form,
                           series=series,
                           **tmpl_args)


@admin_bp.route('/deleteimage/<image_id>', methods=['POST'])
@login_required
@auth_token_required
def delete_image(image_id):
    if not request.is_xhr:
        raise NotFound

    try:
        image = Image.query.get(image_id)
    except:
        current_app.log_exception(sys.exc_info())
        flash('The image could not be deleted')
        return jsonify({'next': url_for('Admin.edit_image',
                                        image_id=image_id)})

    if not image:
        current_app.log_exception(sys.exc_info())
        flash('The image could not be deleted')
        return jsonify({'next': url_for('Admin.edit_image',
                                        image_id=image_id)})

    series_id = image.series.id

    try:
        db.session.delete(image)

        img_root = current_app.config['STATIC_IMAGE_ROOT']
        thumb_root = current_app.config['STATIC_THUMBNAIL_ROOT']
        img_path = Path(img_root, image.filename)
        thumb_path = Path(thumb_root, image.filename)

        img_path.unlink()
        thumb_path.unlink()

        flash('&ldquo;{}&rdquo; has been permanently deleted'.
              format(image.title))
        db.session.commit()

        msg = '[{}] deleted from [{}]'.format(image.title, image.series.title)
        current_app.logger.info(msg)

        return jsonify({'next': url_for('Admin.edit_series',
                                        _id=str(series_id))})
    except:
        current_app.log_exception(sys.exc_info())
        flash('&ldquo;{}&rdquo; could not be deleted'.format(image.title))
        return jsonify({'next': url_for('Admin.edit_image',
                                        image_id=image_id)})
