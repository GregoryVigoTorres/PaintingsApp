import pprint

from flask import render_template, request, abort

from ..core import (db, public_bp)
from ..models.public import Series, Image

_pr = pprint.PrettyPrinter()
pr = _pr.pprint

@public_bp.route('/')
@public_bp.route('/index')
@public_bp.route('/index/<title>')
def index(title=None):
    """ 
    page is 0 indexed current page

    I suspect there's a more efficient way of offsetting and limiting the images,
    but this is OK for now.

    Make this handle AJAX requests
    Load images in a container after the images that are already there, maybe

    """
    try:
        # a carefully crafted request could crash the app
        page = int(request.args.get('page', 0))
    except:
        page = 0

    Limit = 10

    if title:
        sq = db.session.query(Series).filter(Series.title == title).first()
    else:
        sq = db.session.query(Series).order_by(Series.order).limit(1).first()

    if sq is None:
        abort(404)

    img_count = sq.images.count()
    images = sq.images.order_by(Image.order).offset(Limit*page).limit(Limit).all()

    last_page = int(img_count/Limit)

    return render_template('public_index.html', 
                           images=images, 
                           img_count=img_count, 
                           page=page,
                           last_page=last_page)

