import sys
import logging
from pathlib import Path

from flask import (render_template,
                   request,
                   redirect,
                   url_for,
                   current_app,
                   flash,
                   session,
                   jsonify)

from flask.ext.security.decorators import (login_required, auth_token_required)
from flask.ext.login import current_user

from werkzeug.exceptions import NotFound 

from sqlalchemy.orm import joinedload

from .forms.series import SeriesForm
from .utils import (json_token_required, update_model_from_form)
from App.lib.utils import flash_form_errors
from ..core import (db, admin_bp)
from ..models.public import Series, Image


@admin_bp.route('/newseries', methods=['GET', 'POST'])
@login_required
def newseries():
    form = SeriesForm()
    s = Series().query.all()
    form.order.data = len(s)+1

    series = Series()

    if form.validate_on_submit():
        db.session.add(series)
        series = update_model_from_form(series, form)
        msg = '<strong>{}</strong> has been added to series'.format(form.title.data)
        flash(msg)

        msg = '[{}] added to series'.format(form.title.data)
        current_app.logger.info(msg)

        db.session.commit()
        form = SeriesForm()
        return redirect(url_for('.index'))

    if len(form.errors) > 0:
        flash_form_errors(form.errors)
        return redirect(url_for('.newseries'))

    return render_template('admin_series.html', form=form, series=series, 
                           title='Add a new series')


@admin_bp.route('/deleteseries/<_id>', methods=['POST'])
@auth_token_required
@login_required
def delete_series(_id):
    """ ajax only """
    try:
        series = Series.query.filter_by(id=_id).first()
    except:
        current_app.log_exception(sys.exc_info())
        return jsonify({'message':'series not found'})

    if not series:
        return jsonify({'message':'series not found'})

    img_path = Path(current_app.config['STATIC_IMAGE_ROOT'])
    thumb_path = Path(current_app.config['STATIC_THUMBNAIL_ROOT'])

    image_count = len(series.images.all())
    # remove the images in this series as well
    for i in series.images.all():
        i_path = Path(img_path, i.filename)

        if i_path.exists():
            i_path.unlink()

        th_path = Path(thumb_path, i.filename)

        if th_path.exists():
            th_path.unlink()

        db.session.delete(i)

    db.session.delete(series)
    db.session.commit()

    flash('{} and {} images have been permanently deleted'.format(series.title, 
                                                                  image_count))

    msg = '[{}] and {} images permanently deleted'.format(series.title, image_count)
    current_app.logger.info(msg)

    next_url = {'next':url_for('Admin.index')}
    return jsonify(next_url)


@admin_bp.route('/saveimageorder', methods=['POST'])
@auth_token_required
@login_required
def save_image_order():
    if not request.is_xhr:
        raise NotFound

    series_id = request.json.get('series_id')
    updated_images = request.json.get('images') 

    try:
        series = Series.query.get(series_id)
    except:
        current_app.log_exception(sys.exc_info())
        return jsonify({'message':'There was an error updating the image order'})

    for i in series.images.all():
        db.session.add(i)
        i.order = updated_images.get(str(i.id))

    try:
        db.session.commit()
        return jsonify({'message':'Image order updated'})
    except:
        current_app.log_exception(sys.exc_info())
        return jsonify({'message':'There was an error updating the image order'})


@admin_bp.route('/updateseriesorder', methods=['POST'])
@auth_token_required
@login_required
def update_series_order():
    """ AJAX """
    if not request.is_xhr:
        abort(401)

    series_data = request.get_json()
    
    if not series_data:
        return jsonify({'error':'no data'})

    for _id, order in series_data.items():
        series = Series.query.get(_id)
        series.order = int(order) 
    
    db.session.commit()

    return jsonify({
        'message': 'Series order updated'
    })


@admin_bp.route('/editseries/<_id>', methods=['GET', 'POST'])
@login_required
def edit_series(_id):
    """ Edit an existing series by id. 

        Since Images are loaded dynamically so
        they can be offset and limited, 
        images.medium have to loaded joined
        otherwise, they can't be accessed in the
        template, for some reason.
    """
    try:
        series = db.session.query(Series).\
                filter_by(id=_id).first()

        images = series.images.options(joinedload(Image.medium)).all()
    except Exception as E:
        current_app.logger.debug(E)
        flash('series not found')
        return redirect(url_for('Admin.newseries'))

    if not series:
        flash('series not found')
        return redirect(url_for('Admin.newseries'))

    form = SeriesForm(obj=series)

    if form.validate_on_submit():
        updated_series = update_model_from_form(series, form)
        db.session.add(updated_series)
        db.session.commit()

        flash('{} has been modified'.format(updated_series.title))
        msg = 'Series [{}] modified'.format(updated_series.title)
        current_app.logger.info(msg)

        return redirect(url_for('Admin.edit_series', _id=_id))

    if len(form.errors) > 0:
        flash_form_errors(form.errors)
        return redirect(url_for('Admin.edit_series', _id=_id))

    return render_template('admin_edit_series.html', 
                           series=series, 
                           images=images,
                           form=form, 
                           title='Edit {}'.format(series.title))
