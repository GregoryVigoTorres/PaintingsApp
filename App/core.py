from functools import partial
from pathlib import Path
import logging

from flask import (Blueprint, 
                   current_app, 
                   request_finished, 
                   request_started,
                   _request_ctx_stack,
                   session)

from flask.ext.sqlalchemy import SQLAlchemy
from flask_security.core import current_user
from sqlalchemy.ext.declarative import declarative_base
db = SQLAlchemy()
Base = declarative_base()

# There is a circular import here
from App.models.public import Series


def _bp_factory(mod_name, url_prefix, config_args=None, app=None, **kwargs):
    """ blueprint factory """    

    import_name = 'App.{}'.format(mod_name)

    options = {'template_folder':'App/{}/templates'.format(mod_name), 
               'static_folder':'App/{}/static'.format(mod_name), 
               'url_prefix':url_prefix}

    args_from_config = {}

    if app and config_args:
        # get values from app.config that need app context
        # and update options dict 
        for opt_name, val_name in config_args.items():
            conf_val = config_args.get(val_name)
            if conf_val:
                args_from_config[opt_name] = conf_val
       
    if args_from_config:
        options.update(args_from_config)

    if kwargs:
        options.update(kwargs)

    bp = Blueprint(mod_name, import_name, **options) 
    return bp

def load_blueprints(app):
    """ partials are called with app context and registered,
        blueprints are just registered
    """
    with app.app_context():
        for i in Blueprints:
            if isinstance(i, partial):
                kwargs = {}
                if i.keywords.get('config_args'):
                    # get values from config_args to look up in app.config
                    #  and use it to call target func
                    for key, cf in i.keywords.get('config_args').items():
                        val = app.config[cf]
                        kwargs[key] = val

                bp = i(app=app, **kwargs)
                app.register_blueprint(bp)

            if isinstance(i, Blueprint):
                app.register_blueprint(i)


admin_bp = _bp_factory('Admin', '/admin')
public_bp = _bp_factory('Public', '/public')

thumbnails_part = partial(_bp_factory, 
                          'Thumbnails', 
                          '/images', 
                          config_args={'static_folder':'STATIC_THUMBNAIL_ROOT'}) 

images_part = partial(_bp_factory, 
                      'Images', '', 
                      config_args={'static_folder':'STATIC_IMAGE_ROOT'}) 

Blueprints = [admin_bp, public_bp, images_part, thumbnails_part]


def no_cookie(app, **kwargs):
    """ Clear cookie before sending response 
        Except for Admin blueprint 
        or when a csrf token is in the session
    """
    if app.testing:
        return None

    bp = _request_ctx_stack.top.request.blueprint
    # don't unset cookie if csrf_token in session 
    has_csrf = session.get('csrf_token')

    if bp != 'Admin' or has_csrf is None:
        response = kwargs['response']
        del response.headers['Set-Cookie']


def get_all_series():
    """ template global 
    """
    all_series = db.session.query(Series.title, Series.id).order_by(Series.order).all()
    return all_series


def add_auth_token():
    """ make current_user auth token available in templates """
    __name__ = 'get_auth_token'
    with current_app.app_context():
        if current_user and current_user.is_authenticated:
            return current_user.get_auth_token()

def setup_logger(app):
    """ Setup logging handlers FileLogger and EmailLogger """
    if app.debug:
        app.logger.setLevel(10)

    log_fmt_str = '[{levelname}] {asctime} [{name}] {msg}'
    log_fmt = logging.Formatter(fmt=log_fmt_str, style='{')
    
    log_path = Path(app.config['APP_LOGDIR'], app.config['APP_LOGFILE'])

    if not log_path.exists():
        log_path.touch()

    fhandler = logging.handlers.RotatingFileHandler(str(log_path), 
                                                    maxBytes=48600, 
                                                    backupCount=3, 
                                                    delay=True)
    fhandler.setLevel(10)
    fhandler.setFormatter(log_fmt)
    if not app.debug:
        # Only log to file if not in debug i.e. dev mode
        app.logger.addHandler(fhandler)


admin_bp.add_app_template_global(add_auth_token, name='get_auth_token')
admin_bp.add_app_template_global(get_all_series, name='all_series')
request_finished.connect(no_cookie)
