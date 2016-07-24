import uuid
from pathlib import Path
import sys

from flask import (render_template,
                   redirect,
                   request,
                   url_for,
                   flash,
                   jsonify,
                   current_app)


from flask_security.decorators import (login_required, auth_token_required) 

from werkzeug.exceptions import NotFound 

from .forms.image import (ImageForm, EditImageForm)
from .utils import (save_image, upsert_image_from_form)

from App.lib.utils import flash_form_errors
from ..core import (db, admin_bp) 
from ..models.public import Series, Image


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
    tmpl_args = {'page_title':'add a new image to &ldquo;{}&rdquo;'.format(series.title)}

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

    return render_template('admin_image.html', form=form, series=series, **tmpl_args)


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
        'page_title':"""
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
    return render_template('admin_image.html', form=form, series=series, **tmpl_args)


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
        return jsonify({'next':url_for('Admin.edit_image', image_id=image_id)})

    if not image:
        current_app.log_exception(sys.exc_info())
        flash('The image could not be deleted')
        return jsonify({'next':url_for('Admin.edit_image', image_id=image_id)})

    series_id = image.series.id

    try:
        db.session.delete(image)

        img_root = current_app.config['STATIC_IMAGE_ROOT']
        thumb_root = current_app.config['STATIC_THUMBNAIL_ROOT']
        img_path = Path(img_root, image.filename)
        thumb_path = Path(thumb_root, image.filename)

        img_path.unlink()
        thumb_path.unlink()

        flash('&ldquo;{}&rdquo; has been permanently deleted'.format(image.title))
        db.session.commit()

        msg = '[{}] deleted from [{}]'.format(image.title, image.series.title)
        current_app.logger.info(msg)

        return jsonify({'next': url_for('Admin.edit_series', _id=str(series_id))})
    except:
        current_app.log_exception(sys.exc_info())
        flash('&ldquo;{}&rdquo; could not be deleted'.format(image.title))
        return jsonify({'next':url_for('Admin.edit_image', image_id=image_id)})
