# from pathlib import Path # for mk_tmp_dir

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

from .core import (db, load_blueprints)
from .app_setup import (init_db, setup_dirs)
from .models.user import (User, Role, user_datastore)
from .Security import user
from .Admin import (index, series, images, texts, contact)
from Paintings.Public import (index, contact, texts)
from .lib.template_filters import fmt_datetime, none_as_str 

csrf = CsrfProtect()

def create_app(config=None):
    """ config should be a python file """
    app = Flask(__name__.split('.')[0], instance_relative_config=True)

    app.config.from_object('config')
    app.config.from_pyfile('config.py')

    if config is not None:
        app.config.from_pyfile(config)
        app.logger.info('loading config from: {}'.format(config))

    db.init_app(app)

    load_blueprints(app)
    before_first_request_funcs = [setup_dirs(app), 
                                  init_db(app)] 

    #Security
    csrf.init_app(app)
    security = Security()
    security.init_app(app, user_datastore, register_blueprint=False)

    # Assets
    assets = Environment()
    assets.init_app(app)

    jquery = Bundle('js/jquery-2.1.3.min.js', output='js/JQuery.js')
    assets.register('jquery', jquery)

    css = Bundle('css/normalize.css', output='css/base.css')
    assets.register('css', css)

    security_bundle = Bundle('assets/security.scss', filters='scss', output='css/security.css')
    assets.register('security', security_bundle)

    admin_bundle = Bundle('Admin/assets/admin_style.scss', filters='scss', output='static/admin.css')
    assets.register('admin', admin_bundle)

    public_bundle = Bundle('Public/assets/properties.scss', 
                            'Public/assets/nav.scss', 
                            'Public/assets/public.scss',
                            'Public/assets/viewer.scss',
                           filters='scss', output='static/public.css')
    assets.register('public', public_bundle)

    app.add_template_filter(fmt_datetime)
    app.add_template_filter(none_as_str)

    return app


app = create_app()

