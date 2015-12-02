from pathlib import Path
from .core import db, admin_bp
from .models.public import Series

def init_db(app): 
    with app.app_context(): 
        db.create_all() 

def setup_dirs(app):
    with app.app_context():
        req_dirs = ['STATIC_THUMBNAIL_ROOT', 'APP_TMP', 'STATIC_IMAGE_ROOT']
        for dirname in req_dirs:
            path = app.config[dirname]
            dirpath = Path(path)
            if not dirpath.exists():
                dirpath.mkdir(parents=True)
