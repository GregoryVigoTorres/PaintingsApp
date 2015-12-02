import re
from pathlib import Path
import os
from itertools import chain

from flask.ext.script import (Command, prompt, prompt_pass)
from flask import current_app

from Paintings.core import db
from Paintings.models.public import Image

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
