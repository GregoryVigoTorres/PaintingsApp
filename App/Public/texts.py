
from flask import render_template

from ..core import public_bp
from ..models.public import Text, Link 

@public_bp.route('/textlink')
def text_link():
    texts = Text.query.all()
    links = Link.query.all()
    return render_template('public_text.html', texts=texts, links=links) 

@public_bp.route('/text/<_id>')
def text_by_id(_id):
    text = Text.query.get(_id)
    return render_template('single_text.html', text=text)
