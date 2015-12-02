from flask import render_template

from ..core import public_bp
from ..models.public import Contact 

@public_bp.route('/contact')
def contact():
    contact_info = Contact.query.all()
    
    emails = [i for i in contact_info if i.email]
    social_media = [i for i in contact_info if i.name]  

    return render_template('public_contact.html', emails=emails, social_media=social_media) 
