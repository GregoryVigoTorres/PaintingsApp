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


csrf = CsrfProtect()

def create_app(config=None):
    """ config should be a python file """
    from .core import (db, load_blueprints, setup_logger)
    from .app_setup import (init_db, setup_dirs)
    from .models.user import (User, Role, user_datastore)
    from .lib.template_filters import fmt_datetime, none_as_str 

    from .Security import user
    from .Admin import (index, series, images, texts, contact)
    from .Public import (index, contact, texts)

    app = Flask(__name__.split('.')[0], instance_relative_config=True)

    app.config.from_object('config')
    app.config.from_pyfile('config.py')

    setup_logger(app) 

    if config is not None:
        app.config.from_pyfile(config)
        app.logger.info('Started with config from: {}'.format(config))

    # logging
    log_path = Path(app.config['APP_LOGDIR'], app.config['APP_LOGFILE'])
    app.logger.info('Log file path: {}'.format(log_path))

    db.init_app(app)
    load_blueprints(app)
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


    return app
