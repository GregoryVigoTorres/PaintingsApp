"""
Manage database related issues, 
such as removing unused image files
fixing order sequence
"""

import glob
import logging
import os
import uuid

from flask.ext.script import (Command, prompt, prompt_pass)
from flask import current_app
from sqlalchemy import or_
from werkzeug.datastructures import FileStorage

from App.models.public import Image, Series 
from App.core import db
from App.Admin.forms.image import ImageForm
from App.Admin.utils import upsert_image_from_form, save_image



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


class UpdatePrismDate(Command):
    def run(self):
        """ 
        choose series
        has to be prisms type series
        """
        series_objs = Series.query.order_by('order').all()
        for i in series_objs:
            print('{}] {}'.format(i.order, i.title))

        series_order = input('Choose a series> ')

        _series = [i for i in series_objs if i.order == int(series_order)]
        if not _series:
            print('{} is not a valid series'.format(series_order))
            return None
        series = _series[0]

        for i in series.images:
            try:
                date = int(i.title[4:8])
                i.date = date
                db.session.add(i)
                print('Updating {} to {}'.format(i.title, date))
            except Exception as E:
                print('Cannot update {} because:'.format(i.title))
                print(E)

        db.session.commit()
                

class BulkImageUpload(Command):
    """ Image titles are derived from filenames """

    def get_image_title(self, path):
        """ 
        Title is filename without suffix
        """
        fn = os.path.basename(path)
        title = fn.rsplit('.')[0]
        return title

    def upload_images(self, paths, series):
        """
        Create database records
        Derive title from filename
        Get dimensions and medium, use defaults
        Process and move files to static directory 
        Use App functionality, i.e. ImageForm and utils.save_image
        """
        dim_input= input('dimensions w x h in cm (default 21 x 27)> ')
        if dim_input and ' ' in dim_input:
            dimensions = [int(i) for i in dim_input.split()]
        else:
            dimensions = [21, 27]

        medium = input('medium (default Acrylic on paper)> ') or 'Acrylic on paper'
        padding_color = input('padding color (default #fff)> ') or '#fff'

        # save to disk first to get filename
        for i in paths:
            title = self.get_image_title(i)
            date = int(title[4:8])

            with open(i, mode='rb') as fd:
                img_fs = FileStorage(filename=os.path.basename(i), 
                                     name='image',
                                     content_type='image/jpeg',
                                     stream=fd)

                filename = save_image(img_fs)

            form_data = {'title':title,
                         'id':uuid.uuid4(),
                         'filename':filename,
                         'series_id':series.id,
                         'medium':medium,
                         'date':date,
                         'dimensions':dimensions,
                         'padding_color':padding_color}

            form = ImageForm(data=form_data)
            img = upsert_image_from_form(form)
            print(img, img.id, img.filename)

        db.session.commit()


    def run(self):
        """ 
            Get or create series
            Point to directory with images
            Get titles from filenames
            Don't upload images recursively
            Set default properties, like dimensions, medium
        """
        series_objs = Series.query.order_by('order').all()
        print('0] new series')
        for i in series_objs:
            print('{}] {}'.format(i.order, i.title))

        series_order = input('Choose a series> ')

        # new series
        if series_order == '0':
            nseries = Series()
            db.session.add(nseries)
            title = input('Series title> ')
            nseries.title = title
            last_obj = max(series_objs, key=lambda i: i.order)
            nseries.order = last_obj.order + 1
            db.session.commit()
            print('Created {}'.format(nseries))
            series = nseries
        else:
            _series = [i for i in series_objs if i.order == int(series_order)]
            if not _series:
                print('{} is not a valid series'.format(series_order))
                return None
            series = _series[0]

        src_dir = input('Absolute path to image directory> ')

        # TEST DIR
        # src_dir = "/home/lemur/Desktop/documentation_7_16/prisms/corrected"

        if not os.path.exists(src_dir):
            print('That directory doesn\'t exist')
            return None

        glob_rule = input('file filter glob (default *.jpeg)> ') or '*.jpeg'

        # TEST glob rule
        # glob_rule = '*.jpeg'
        pathspec = src_dir+'/'+glob_rule
 
        # get filtered files
        paths = glob.iglob(pathspec, recursive=False)
        if not paths:
            print('No matching files found')
            return None
        images = self.upload_images(paths, series)

