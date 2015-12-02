from pathlib import Path

from flask import (render_template,
                   redirect,
                   url_for,
                   current_app,
                   flash,
                   jsonify)

from flask.ext.security.decorators import (login_required, auth_token_required)

from sqlalchemy.orm import joinedload

from .forms.series import SeriesForm
from .utils import (json_token_required, update_model_from_form)
from Paintings.lib.utils import flash_form_errors
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
        current_app.logger.info(msg)
        flash(msg)
        db.session.commit()
        form = SeriesForm()

    if len(form.errors) > 0:
        flash_form_errors(form.errors)
        return redirect(url_for('.newseries'))

    return render_template('admin_series.html', form=form, series=series, 
                           title='Add a new series')


@admin_bp.route('/deleteseries/<_id>', methods=['POST'])
@auth_token_required
def delete_series(_id):
    """ ajax only """
    series = Series.query.filter_by(id=_id).first()

    if not series:
        return jsonify({'message':'series not found'})

    img_path = Path(current_app.config['STATIC_IMAGE_ROOT'])
    thumb_path = Path(current_app.config['STATIC_THUMBNAIL_ROOT'])

    # remove the images in this series as well
    for i in series.images:
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
                                                                  len(series.images)))

    next_url = {'next':url_for('Admin.index')}
    return jsonify(next_url)


@admin_bp.route('/editseries/<_id>', methods=['GET', 'POST'])
@login_required
@json_token_required
def edit_series(_id):
    """ edit an existing series by id """
    series = db.session.query(Series).options(
        joinedload(Series.images).joinedload(Image.medium)
        ).filter_by(id=_id).first()

    if not series:
        flash('Oops!')
        flash('series not found')
        return redirect(url_for('Admin.newseries'))

    form = SeriesForm(obj=series)

    if form.validate_on_submit():
        updated_series = update_model_from_form(series, form)
        db.session.add(updated_series)
        db.session.commit()
        flash('{} has been modified'.format(updated_series.title))

        return redirect(url_for('Admin.edit_series', _id=_id))

    if len(form.errors) > 0:
        flash_form_errors(form.errors)
        return redirect(url_for('Admin.edit_series', _id=_id))

    return render_template('admin_edit_series.html', 
                           series=series, 
                           form=form, 
                           title='Edit {}'.format(series.title))
