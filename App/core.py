# from functools import partial
from pathlib import Path
import logging

from colorama import Fore, Back, Style
from colorama import init as init_colorama
init_colorama(autoreset=True)

from flask import (Blueprint, 
                   current_app, 
                   request_finished, 
                   request_started,
                   _request_ctx_stack,
                   session)

from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
db = SQLAlchemy()
Base = declarative_base()

from App.lib.template_globals import (
    get_all_series, 
    get_auth_token)


def _bp_factory(mod_name, url_prefix, config_args=None, app=None, **kwargs):
    """ blueprint factory """    

    import_name = 'App.{}'.format(mod_name)

    options = {'template_folder':'App/{}/templates'.format(mod_name), 
               'static_folder':'App/{}/static'.format(mod_name), 
               'static_url_path':'/{}/static'.format(mod_name.lower()),
               'url_prefix':url_prefix}

    args_from_config = {}

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
            if isinstance(i, Blueprint):
                app.register_blueprint(i)


## mod_name, url_prefix
admin_bp = _bp_factory('Admin', '/admin')
public_bp = _bp_factory('Public', None)
## don't use values from app.config
thumbnails_bp = _bp_factory('Thumbnails', '/images', static_folder='images/thumbnails') 
images_bp = _bp_factory('Images', '', static_folder='images')

Blueprints = [admin_bp, public_bp, images_bp, thumbnails_bp]


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


def setup_logger(app):
    """ Setup logging handlers FileLogger and EmailLogger """
    if app.debug:
        app.logger.setLevel(10)

    # get fmt string from config
    if app.config.get('LOG_FORMAT'):
        log_fmt_str = app.config['LOG_FORMAT']
    else:
        log_fmt_str = '[{levelname}] {asctime} [{name}] {msg}'
    
    log_fmt = logging.Formatter(fmt=log_fmt_str, style='{')
    app.logger.handlers[0].setFormatter(log_fmt)

    # file logging
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
        app.logger.info('Log file path: {}{}'.format(Fore.CYAN, log_path))

# add template globals to blueprints
admin_bp.add_app_template_global(get_auth_token, name='get_auth_token')
admin_bp.add_app_template_global(get_all_series, name='all_series')
request_finished.connect(no_cookie)
