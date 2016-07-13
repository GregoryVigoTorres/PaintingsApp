import re
from pathlib import Path
import os
from itertools import chain

from flask.ext.script import (Command, prompt, prompt_pass)
from flask import current_app

from App.core import db
from App.models.public import Image, Series

class UnusedFiles(Command):
    def __init__(self):
        self.app = current_app

    def run(self):
        """ Query db for images and scan static dirs for files
            Remove unused files (mostly images added during development/testing)
            and potentially unused css or js files
        """
        img_root = self.app.config['STATIC_IMAGE_ROOT']
        # STATIC_THUMBNAIL_ROOT ## is beneath img_root
        image_q = db.session.query(Image.filename).all()
        images_fn = [i[0] for i in sorted(image_q, key=lambda i:i[0])]

        img_paths = chain.from_iterable([[Path(r, fn) for fn in f] for r, d, f in os.walk(img_root)])
        del_paths = [i for i in img_paths if i.name not in images_fn]
        
        for i in sorted(del_paths, key=lambda i:i.name) :
            print('deleting {}'.format(i))
            i.unlink()


class ValidatePrismTitles(Command):
    def validate_title(self, image):
        title = image.title
        valid = True
        reason = None

        if len(title) != 14:
            reason = '{} does not have 14 characters'.format(title)
            valid = False

        dd = int(title[0:2])
        MM = int(title[2:4])
        yyyy = int(title[4:8])
        hh = int(title[8:10])
        mm = int(title[10:12])
        ss = int(title[12:14])

        if dd > 31 or dd < 1:
            valid = False
        if MM > 12 or MM < 1:
            valid = False
        if yyyy < 2014 or yyyy > 2017:
            valid = False
        if hh > 24 or hh < 1:
            valid = False
        if mm > 60:
            valid = False
        if ss > 60:
            valid = False
        if valid is False:
            if reason:
                print('{} ({}) is not a valid title because {}'.format(title, image.filename, reason))
            else:
                print('{} ({}) is not a valid title'.format(title, image.filename))


    def run(self):
        """
        ddmmyyyyhhmmss
        Only makes sure that values are within bounds 
        and there are no extra characters
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
            self.validate_title(i)
        print('All titles in {} validated'.format(series.title))


class MakeRobotsTxt(Command):
    def __init__(self):
        self.app = current_app
        self.robot_txt = ['User-agent: *']

    def run(self):
        """ Make sure all admin and static urls are disallowed for all user agents
        """
        url_arg_re = re.compile('/(<.*>)')        

        for i in self.app.url_map.iter_rules():
            if not i.endpoint.startswith('Public'):
                url_n = re.subn(url_arg_re, '', str(i))
                url = url_n[0]

                if url_n[1]:
                    self.robot_txt.append('Disallow: {}/'.format(url))
                else:
                    self.robot_txt.append('Disallow: {}'.format(url))

        print('>created robots.txt as...')
        robots = '\n'.join(self.robot_txt)
        print(robots)

        root = Path(current_app.config['APP_ROOT'])
        fn = Path(root, 'robots.txt')
        
        with fn.open(mode='w') as fd:
            fd.write(robots)
