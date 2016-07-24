from flask import (render_template,
                   redirect,
                   request,
                   url_for,
                   flash,
                   jsonify)

from flask_security.decorators import (login_required, auth_token_required) 

from werkzeug.exceptions import NotFound 

from App.Admin.forms.text import (TextForm, LinkForm)
from .utils import update_model_from_form

from App.lib.utils import flash_form_errors
from App.core import (db, admin_bp) 
from App.models.public import Text, Link 


@admin_bp.route('/textslinks', methods=['GET'])
@login_required
def texts_links():
    tmpl_args = {'page_title':'all texts and links'}
    texts = db.session.query(Text).all()
    links = db.session.query(Link).all()

    return render_template('admin_texts_links.html', texts=texts, links=links, **tmpl_args) 


@admin_bp.route('/newtextlink', methods=['GET', 'POST'])
@login_required
def new_text_link():
    """
       new text OR link 
    """
    text_form = TextForm()
    link_form = LinkForm()
    tmpl_args = {'page_title':'add a new text or link'}

    if request.method == 'POST':
        form = None
        if request.form['name'] == 'text':
            form = text_form
            model = Text()
            next_url = url_for('Admin.edit_text', text_id=text_form.id.data)
        if request.form['name'] == 'link':
            form = link_form
            model = Link()
            next_url = url_for('Admin.edit_link', link_id=link_form.id.data)

        if not form:
            return render_template('admin_text.html', 
                                   text_form=text_form, 
                                   link_form=link_form, 
                                   **tmpl_args)
            
        valid = form.validate()
        if not valid:
            flash_form_errors(form.errors)
        else:
            model = update_model_from_form(model, form)
            db.session.add(model)
            db.session.commit()
            name = form.data.get('title') or form.data.get('label')
            flash('<strong>{}</strong> has been added'.format(name))
            msg = '[{}] added to texts/links'.format(name)
            current_app.logger.info(msg)

            return redirect(next_url)

    return render_template('admin_text.html', 
                           text_form=text_form, 
                           link_form=link_form, 
                           **tmpl_args)


@admin_bp.route('/edittext/<text_id>', methods=['GET', 'POST'])
@login_required
def edit_text(text_id):
    """
       edit text
    """
    try:
        text = Text.query.get(text_id)
    except:
        flash('The text couldn\'t be found')
        raise NotFound()
    
    if not text:
        raise NotFound()

    if request.method == 'GET':
        form = TextForm(obj=text)

    if request.method == 'POST':
        form = TextForm(request.form)
    
    if form.validate_on_submit():
        db.session.add(text)
        text = update_model_from_form(text, form)
        db.session.commit()
        flash('<strong>&ldquo;{}&rdquo;</strong> has been updated'.format(text.title))
        msg = 'Text [{}] updated'.format(text.title)
        current_app.logger.info(msg)

        return redirect(url_for('Admin.edit_text', text_id=text_id))

    if len(form.errors):
        flash_form_errors(form.errors)

    tmpl_args = {'page_title': 'edit &ldquo;{}&rdquo;'.format(text.title)}

    return render_template('admin_edit_text.html', text=text, form=form, **tmpl_args)

@admin_bp.route('/editlink/<link_id>', methods=['GET', 'POST'])
@login_required
def edit_link(link_id):
    """
       edit link 
    """
    try:
        link = Link.query.get(link_id)
    except:
        flash('The link couldn\'t be found')
        raise NotFound()

    if not link:
        raise NotFound

    if request.method == 'GET':
        form = LinkForm(obj=link)

    if request.method == 'POST':
        form = LinkForm(request.form)
    
    if form.validate_on_submit():
        db.session.add(link)
        link = update_model_from_form(link, form)
        db.session.commit()
        flash('<strong>&ldquo;{}&rdquo; has been updated</strong>'.format(link.label))
        msg = 'Link [{}] updated'.format(link.label)
        current_app.logger.info(msg)

        return redirect(url_for('Admin.edit_link', link_id=link_id))

    if len(form.errors):
        flash_form_errors(form.errors)

    tmpl_args = {'page_title': 'edit &ldquo;{}&rdquo;'.format(link.label)}

    return render_template('admin_edit_link.html', link=link, form=form, **tmpl_args)


@admin_bp.route('/deletetext/<text_id>', methods=['POST'])
@login_required
@auth_token_required
def delete_text(text_id):
    """
       delete text
       this is ajax
    """
    if not request.is_xhr:
        raise NotFound()

    try:
        text = Text.query.get(text_id)
    except:
        flash('The link couldn\'t be found')
        raise NotFound()

    if not text:
        raise NotFound()

    msg = '{} has been permanently deleted'.format(text.title)

    db.session.add(text)
    db.session.delete(text)
    db.session.commit()
    flash(msg)

    msg = '[{}] deleted from texts'.format(text.title)
    current_app.logger.info(msg)

    return jsonify({'next': url_for('Admin.texts_links')})


@admin_bp.route('/deletelink/<link_id>', methods=['POST'])
@login_required
@auth_token_required
def delete_link(link_id):
    """
       delete link
       this is ajax
    """
    if not request.is_xhr:
        raise NotFound()

    try:
        link = Link.query.get(link_id)
    except:
        flash('The link couldn\'t be found')
        raise NotFound()

    if not link:
        raise NotFound()

    msg = '{} has been permanently deleted'.format(link.label)

    db.session.add(link)
    db.session.delete(link)
    db.session.commit()
    flash(msg)

    msg = '[{}] deleted from links'.format(link.label)
    current_app.logger.info(msg)

    return jsonify({'next': url_for('Admin.texts_links')})
