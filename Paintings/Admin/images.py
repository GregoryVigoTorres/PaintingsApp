from flask import (render_template,
                   redirect,
                   request,
                   url_for,
                   flash,
                   jsonify)

from flask.ext.security.decorators import (login_required, auth_token_required) 

from werkzeug.exceptions import NotFound 

from .forms.image import (ImageForm, EditImageForm)
from .utils import (save_image, upsert_image_from_form)

from Paintings.lib.utils import flash_form_errors
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
    series = Series.query.filter_by(id=series_id).first()
    if not series:
        raise NotFound()
    
    form = ImageForm()
    tmpl_args = {'page_title':'add a new image to &ldquo;{}&rdquo;'.format(series.title)}

    if form.validate_on_submit():
        image = upsert_image_from_form(form)
        filename = save_image(request.files['image'])

        if filename:
            image.filename = filename
            db.session.commit()
            flash('{} <br>added to {}'.format(image.title, image.series.title))
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
    image = Image.query.filter_by(id=image_id).first()

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

        return redirect(url_for('Admin.edit_image', image_id=image.id))

    if len(form.errors) > 0:
        flash_form_errors(form.errors)
        return redirect(url_for('Admin.edit_image', image_id=image.id))
    return render_template('admin_image.html', form=form, series=series, **tmpl_args)


@admin_bp.route('/deleteimage/<image_id>', methods=['POST'])
@login_required
@auth_token_required
def delete_image(image_id):
    # the file needs to be "unlinked"
    if not request.is_xhr:
        raise NotFound

    image = Image.query.get(image_id)
    if not image:
        raise NotFound

    series_id = image.series.id
    db.session.add(image)
    db.session.delete(image)
    db.session.commit()

    flash('&ldquo;{}&rdquo; has been permanently deleted'.format(image.title))

    return jsonify({'next': url_for('Admin.edit_series', _id=str(series_id))})
