from pathlib import Path
from .core import db, admin_bp

def init_db(app): 
    with app.app_context(): 
        db.create_all() 

def setup_dirs(app):
    with app.app_context():
        req_dirs = ['STATIC_THUMBNAIL_ROOT',
                    'APP_TMP',
                    'APP_LOGDIR',
                    'STATIC_IMAGE_ROOT']
        
        for dirname in req_dirs:
            path = app.config[dirname]
            dirpath = Path(path)
            
            if not dirpath.exists():
                dirpath.mkdir(parents=True)
        
        # touch log files
        # App log file is created in core.setup_logger 
        uwsgi_log_fn = Path(app.config['APP_LOGDIR'], 'uwsgi.log')
        try:
            uwsgi_log_fn.touch(exist_ok=False)
            app.logger.info('touched {}'.format(uwsgi_log_fn))
        except FileExistsError:
            pass
