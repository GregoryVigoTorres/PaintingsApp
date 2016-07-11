"""
Manage database related issues, 
such as removing unused image files
fixing order sequence
"""

import curses
import logging
import os
import time

from flask.ext.script import (Command, prompt, prompt_pass)
from flask import current_app
from sqlalchemy import or_

from App.models.public import Image, Series 
from App.core import db



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


class FileBrowser():
    def __init__(self, win, basedir=None):
        self.win = win
        self.basedir = basedir or os.path.expanduser('~')
        self.type_keys = {'3':'d', '2':'f', '1':'l'}
        self.dirlist = self.get_dirlist()
        self.key = None
        # start an event loop
        # listen for key events
        while True:
            pad = curses.newpad(len(self.dirlist), 120)
            pad.addstr('{} items\n'.format(len(self.dirlist)))
            pad.box()
            for i in self.dirlist:
                pad.addstr('[{}] {}'.format(self.type_keys[str(i['type'])], i['name']))

            pad.refresh(0,0, 0,0, 35,120)

            event = pad.getch()
            if event == ord('q'):
                break


    def get_pad(self, lines, cols):
        return curses.newpad(lines, cols)
            
    def get_dirlist(self, rootdir=None):
        """ directories=3, files=2, symlinks=1 """
        root = rootdir or self.basedir
        dl = os.scandir(root)
        dirlist = []
        for i in dl:
            d = {}
            d['name'] = i.name
            if i.is_dir(follow_symlinks=False):
                d['type'] = 3
            if i.is_file(follow_symlinks=False):
                d['type'] = 2
            if i.is_symlink():
                d['type'] = 1
            dirlist.append(d)

        # sort by name then by type
        dirlist.sort(key=lambda i: i['name'])
        dirlist.sort(key=lambda i: i['type'], reverse=True)

        return dirlist



class BulkImageUpload(Command):
    """ Image titles are derived from filenames """

    def update_wins(self):
        for win in self.windows:
            # win.clear()
            win.noutrefresh()
        curses.doupdate()


    def key_listener(self, key, last_line):
        # RETURN = 10
        if key == 10:
            return 1
        
        # EXIT
        # q = 113
        # ESC = 27
        elif key == 113: # in (113, 27):
            return 1

        #  KEY_UP = 259
        elif key == 259 and self.line_hl > 0:
            self.line_hl -= 1

        elif key == 259 and self.line_hl == 0:
            self.line_hl = last_line

        # KEY_DOWN = 258
        elif key == 258 and self.line_hl < last_line:
            self.line_hl += 1

        elif key == 258 and self.line_hl == last_line:
            self.line_hl = 0


    def show_series(self, series_list):
        self.series_win.addstr('Choose a series:\n')
        self.series_win.addstr('0] new series\n')

        for i in series_list:
            self.series_win.addstr('{}] {}\n'.format(i[0], i[1].title))

        self.series_win.hline('.', 25)


    def main(self):
        """ 
        The main event loop 
        and state live here
        """ 
        series = Series.query.all()
        series_list = [(ind, i) for ind, i in enumerate(series, start=1)] 
        last_line = len(series_list)
        # lines, cols
        self.series_win = curses.newwin(len(series_list)+10, 80)

        # Use blocking getch
        self.series_win.timeout(-1)
        self.stdscr.timeout(-1)

        # index of current line choice
        self.line_hl = 0

        self.windows = [self.stdscr, self.series_win]

        self.show_series(series_list)
        self.update_wins()
        key = self.series_win.getch()

        self.stdscr.clear()

        # choose directory of images
        # base_dir = os.path.expanduser('~')
        # self.stdscr.addstr(base_dir)
        # self.stdscr.refresh()
        # # time.sleep(2)
        # key = self.series_win.getch()
        fb = FileBrowser(self.stdscr)


    def run(self):
        """ Setup and Teardown curses """
        try:
            self.stdscr = curses.initscr()
            curses.start_color()
            curses.cbreak()
            self.stdscr.clear()
            self.stdscr.keypad(1)
            self.main()
        except Exception as E:
            print(E)
        finally:
            curses.nocbreak()
            self.stdscr.keypad(0)
            curses.echo()
            curses.endwin()
