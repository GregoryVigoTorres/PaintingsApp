import uuid
import tempfile
import os.path
from pathlib import Path
import re
from functools import wraps

from flask import (current_app, request, _request_ctx_stack)
from flask_security.decorators import _get_unauthorized_response
from flask_principal import (Identity, identity_changed)
from werkzeug import MultiDict
from werkzeug.local import LocalProxy

from PIL import Image as PImage

from App.core import db
from App.models.public import (Series, Medium, Image)

_security = LocalProxy(lambda: current_app.extensions['security'])


def _check_token():
    """ basically copied from flask.security native function """

    json_key = current_app.config['SECURITY_TOKEN_AUTHENTICATION_KEY']
    json_token = request.get_json(silent=True)

    if not json_token:
        return False

    json_data = {i['name']:i['value'] for i in json_token}
    token = json_data.get(json_key)
    if token:
        user = _security.login_manager.token_callback(token)
    else:
        return False

    if user and user.is_authenticated():
        app = current_app._get_current_object()
        _request_ctx_stack.top.user = user
        identity_changed.send(app, identity=Identity(user.id))
        return True

    return False


def json_token_required(fn):
    """ only checks json requests, expects standard jquery serialized json data
    this is basically copied from flask.security native function """
    @wraps(fn)
    def decorated(*args, **kwargs):
        if not request.is_xhr:
            return fn(*args, **kwargs)

        if _check_token():
            return fn(*args, **kwargs)
        else:
            return _get_unauthorized_response()

    return decorated


def jquery_json_to_multidict(jq_json):
    """ MultiDicts can be used to populate forms and orm objects
    """
    mdict = MultiDict()
    mdict.update({i['name']:i['value'] for i in jq_json})
    return mdict


def update_model_from_form(model, form):
    """ model instance, form instance
        Only updates fields where model data does not match form data
        Returns model
    """
    for k, v in form.data.items():
        if hasattr(model, k):
            if getattr(model, k) != form.data[k]:
                setattr(model, k, v)
    return model


def save_image(img):
    """
    As is "save to disk"
    img from request.files.get('image')
    validates and saves image file
    resize
    make thumbnail
    return new filename
    saves all images as jpeg
    """

    allowed_types = ('image/jpeg', 'image/jpg', 'image/png')
    mime_type = img.mimetype
    if mime_type not in allowed_types:
        return None

    pil_type = mime_type.split('/')[1].upper()
    if pil_type == 'JPG':
        pil_type = 'JPEG'

    image_args = {'optimize':True}
    if pil_type == 'JPEG':
        image_args.update({'progressive':True, 'quality':95})

    tmp_dir = Path(current_app.config['APP_TMP'])
    filename = '{}.{}'.format(str(uuid.uuid4()), img.filename)
    fs_path = Path(current_app.config['STATIC_IMAGE_ROOT'], filename)
    th_path = Path(current_app.config['STATIC_THUMBNAIL_ROOT'], filename)

    with tempfile.TemporaryFile(dir=str(tmp_dir)) as tmp:
        img_data = img.stream.read()
        tmp.write(img_data)
        # large
        fullsize = PImage.open(tmp)

        fullsize.thumbnail((450, 450))
        fullsize.save(str(fs_path), pil_type, **image_args)
        # small
        thumb = PImage.open(tmp)
        thumb.thumbnail((220, 220))
        thumb.save(str(th_path), pil_type, **image_args)

    if fs_path.exists() and th_path.exists():
        return filename
    else:
        return None


def save_icon(icon_file):
    """ also validates icon file
        max size = 64px
        overwrites existing file if it has the same name
        ... a lot of this code is repeated...
    """
    allowed_types = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif']
    mime_type = icon_file.mimetype

    if mime_type not in allowed_types:
        return None

    pil_type = mime_type.split('/')[1].upper()
    if pil_type == 'JPG':
        pil_type = 'JPEG'

    image_args = {'optimize':True}

    if pil_type == 'JPEG':
        image_args.update({'progressive':True, 'quality':95})

    icon_root = Path(current_app.config['APP_ROOT'], 'App', 'static', 'icons')

    if not icon_root.exists():
        icon_root.mkdir()

    path = Path(icon_root, icon_file.filename)
    tmp_dir = Path(current_app.config['APP_TMP'])

    with tempfile.TemporaryFile(dir=str(tmp_dir)) as tmp:
        img_data = icon_file.stream.read()
        tmp.write(img_data)
        icon_img = PImage.open(tmp)

        if icon_img.width > 64 or icon_img.height > 64:
            return None

        icon_img.save(str(path), pil_type, **image_args)

    return icon_file.filename


def upsert_image_from_form(form):
    """ creates medium if it doesn't exist already
        adds image and medium to db.session
        filename is added elsewhere
    """
    image = Image.query.filter_by(id=form.data['id']).first()
    if not image:
        image = Image()

    series = Series.query.filter_by(id=form.data['series_id']).first()

    medium_name = form.data.get('medium')

    if medium_name:
        medium = Medium.query.filter_by(name=medium_name).first()
        if not medium:
            medium = Medium(name=medium_name)
    else:
        medium = None

    with db.session.no_autoflush:
        image.series = series

        for k, v in form.data.items():
            try:
                if v and v != getattr(image, k):
                    setattr(image, k, v)
            except AttributeError:
                pass

        if medium:
            setattr(image, 'medium_id', medium.id)
            setattr(image, 'medium', medium)
            db.session.add(medium)

        db.session.add(image)

    return image


def parse_bulk_upload_filename(img, title_re_from, title_re_to, date_re):
    """
    Parse image filename and return title and date using regex rules
    """
    try:
        orig_filename = os.path.splitext(os.path.basename(img.filename))[0]

        # re.sub returns string unchanged if match not found
        # it's possible that a filename already matches the valid title format
        # make sure orig_filename fits the regex criteria,
        # to avoid setting the filename as the title
        # This is only here temporarily as a stop gap
        # until I implement get date from re.sub or set by user as a year
        assert re.search(title_re_from, orig_filename)

        title = re.sub(title_re_from, title_re_to, orig_filename)
        date = re.sub(title_re_from, date_re, orig_filename)

        assert title
        assert date

        return title, date
    except Exception as E:
        current_app.logger.debug('Error parsing filename: {}'.format(E))
        return None, None
