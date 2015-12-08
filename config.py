# Global config to which instance config is appended 
from pathlib import Path

APP_ROOT = str(Path('__file__').parent.resolve())
APP_TMP = str(Path(APP_ROOT, 'tmp'))
APP_LOGDIR = str(Path(APP_ROOT, 'var', 'log'))
STATIC_IMAGE_ROOT = str(Path(APP_ROOT, 'App', 'images'))
STATIC_THUMBNAIL_ROOT = str(Path(APP_ROOT, 'App', 'images', 'thumbnails'))

# use blueprint name instead of LOGIN_URL
SECURITY_BLUEPRINT_NAME = 'Admin'
