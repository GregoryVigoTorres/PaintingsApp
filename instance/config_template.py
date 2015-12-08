# This file contains sensitive information that probably shouldn't be under version control
db_conf = {'role':'',
           'passw':'',
           'port':'',
           'dbname':''}

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{role}:{passw}@localhost:{port}/{dbname}'.format(**db_conf)

SECRET_KEY = '' 

SECURITY_PASSWORD_HASH = 'bcrypt'
SECURITY_PASSWORD_SALT = '' 
SESSION_PROTECTION = 'basic'
SESSION_COOKIE_NAME = ''
