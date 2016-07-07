from pathlib import Path

from flask import (Flask, 
        current_app, 
        g, 
        session, 
        url_for, 
        render_template, 
        flash)

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import (Security, SQLAlchemyUserDatastore)
from flask_wtf.csrf import CsrfProtect
from flask.ext.assets import (Environment, Bundle)

from colorama import Fore, Back, Style
from colorama import init as init_colorama
init_colorama(autoreset=True)

csrf = CsrfProtect()

def create_app(config=None):
    """ config should be a python file """
    from .app_setup import (init_db, setup_dirs)
    from .core import (db, load_blueprints, setup_logger)
    from .lib.template_filters import fmt_datetime, none_as_str 
    from .models.user import (User, Role, user_datastore)

    from .Admin import (index, series, images, texts, contact)
    from .Public import (index, contact, texts)
    from .Security import user

    app = Flask(__name__.split('.')[0], instance_relative_config=True)

    app.config.from_object('config')
    app.config.from_pyfile('config.py')

    if config is not None:
        app.config.from_pyfile(config)
        setup_logger(app) 
        app.logger.info('Started with config from: {}'.format(config))
    else:
        setup_logger(app) 

    # Flask.sqlalchemy
    db.init_app(app)

    load_blueprints(app)
    
    # make sure db tables and required directories exist
    before_first_request_funcs = [setup_dirs(app), 
                                  init_db(app)]

    #Security
    csrf.init_app(app)
    security = Security()
    security.init_app(app, user_datastore, register_blueprint=False)

    # Assets
    assets = Environment(app=app)
    ## TODO add app js to bundles
    ## fix stupid static dirs issue
    assets.from_yaml('assets.yml')
    
    # template filters
    app.add_template_filter(fmt_datetime)
    app.add_template_filter(none_as_str)

    # print(app.url_map)

    return app
