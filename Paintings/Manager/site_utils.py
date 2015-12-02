import re
from pathlib import Path

from flask.ext.script import (Command, prompt, prompt_pass)
from flask import current_app

from Paintings.core import db

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
