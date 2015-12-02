"""
Manage database related issues, 
such as removing unused image files
fixing order sequence
"""

from flask.ext.script import (Command, prompt, prompt_pass)
from flask import current_app
from sqlalchemy import or_

from Paintings.models.public import Image 
from Paintings.core import db



class UpdateOrder(Command):
    """ 
        Update image order to date added
    """
    def run(self):
        """ 
            Set order for images to order images were added 
        """
        
        db_conf = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        if not db_conf:
            print('DB URI not found')
            return None

        db_uri = db_conf.split('/')[-1]
        print('>connected to db: {}'.format(db_uri))

        images = Image.query.order_by(Image.date_created.desc()).all()

        print('\n>images')
        for ind, i in enumerate(images, start=1):
            i.order = ind
            db.session.add(i)
            print('\t{} {} {}'.format(i.title, i.order, i.date_created))

        db.session.commit()
