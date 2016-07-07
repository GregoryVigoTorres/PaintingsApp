# Global config to which instance config is appended 
from pathlib import Path
import os

APP_ROOT = str(Path('__file__').parent.resolve())
APP_TMP = str(Path(APP_ROOT, 'tmp'))
APP_LOGDIR = str(Path(APP_ROOT, 'var', 'log'))
APP_LOGFILE = 'App.log'
STATIC_IMAGE_ROOT = os.path.join(APP_ROOT, 'images')
STATIC_THUMBNAIL_ROOT = os.path.join(APP_ROOT, 'images', 'thumbnails')

# use blueprint name instead of LOGIN_URL
SECURITY_BLUEPRINT_NAME = 'Admin'
