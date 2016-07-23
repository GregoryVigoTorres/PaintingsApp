import sys

from flask import (render_template,
                   redirect,
                   request,
                   url_for,
                   current_app,
                   flash)  

from flask_security.decorators import login_required

from App.Admin.forms.contact import ContactForm
from .utils import (update_model_from_form,
                    save_icon) 

from App.lib.utils import flash_form_errors
from App.core import (db, admin_bp) 
from App.models.public import Contact



@admin_bp.route('/contact', methods=['GET'])
@login_required
def contact():
    tmpl_args = {'page_title':'contact info'}

    emails = db.session.query(Contact.id, Contact.email).filter(Contact.email != '').all()
    profiles = db.session.query(Contact.id, 
                                Contact.name, 
                                Contact.url, 
                                Contact.icon_filename).filter(Contact.name != '').all()

    return render_template('admin_contact.html', emails=emails, profiles=profiles, **tmpl_args)


@admin_bp.route('/editcontact/<_id>', methods=['GET', 'POST'])
@login_required
def edit_contact(_id):
    """edit/update contact or link to social media profile """
    tmpl_args = {'page_title':'edit contact info'}

    try:
        contact_info = Contact.query.get_or_404(_id)
    except:
        current_app.log_exception(sys.exc_info()) 
        return redirect(url_for('Admin.contact'))

    if request.method == 'GET':
        form = ContactForm(obj=contact_info)
    if request.method == 'POST':
        form = ContactForm(request.form)

    if len(contact_info.email):
        tmpl_args['type'] = 'email'
    else:
        tmpl_args['type'] = 'profile'

    filename = contact_info.icon_filename
    tmpl_args['icon_filename'] = filename

    if form.validate_on_submit():
        db.session.add(contact_info)
        update_model_from_form(contact_info, form)

        icon_file = request.files.get('icon')

        if icon_file:
            icon_filename = save_icon(icon_file)
            
            if icon_filename:
                contact_info.icon_filename = icon_filename

        if tmpl_args['type'] == 'email':
            name = contact_info.email
        if tmpl_args['type'] == 'profile':
            name = contact_info.name

        flash('<strong>&ldquo;{}&rdquo;</strong> has been updated'.format(name))
        db.session.commit()

        msg = '[{}] updated'.format(name)
        current_app.logger.info(msg)

        return redirect(url_for('Admin.edit_contact', _id=_id))

    if len(form.errors):
        flash_form_errors(form.errors)

    return render_template('admin_edit_contact.html', form=form, **tmpl_args) 


@admin_bp.route('/newcontact', methods=['GET', 'POST'])
@login_required
def new_contact():
    tmpl_args = {'page_title':'add contact info'}
    form = ContactForm()
    if form.validate_on_submit():
        contact_info = Contact()
        db.session.add(contact_info)
        contact_info = update_model_from_form(contact_info, form)

        icon_file = request.files.get('icon')
        if icon_file:
            icon_filename = save_icon(icon_file)
            
            if icon_filename:
                contact_info.icon_filename = icon_filename

        db.session.commit()
        flash('<strong>{} has been added</strong>'.format(contact_info.name))
        msg = '[{}] added to contact info'.format(contact_info.name)
        current_app.logger.info(msg)

        return redirect(url_for('Admin.contact'))

    if len(form.errors):
        flash_form_errors(form.errors)

    return render_template('admin_new_contact.html', form=form, **tmpl_args)
