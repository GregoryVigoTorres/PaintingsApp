#! /usr/bin/env python3

from flask.ext.script import Manager
from App.App import create_app
from App.Manager.Users import (CreateUser, DeleteUser)
from App.Manager.DbUtils import UpdateOrder
from App.Manager.site_utils import UnusedFiles

manager = Manager(create_app)
manager.add_option('-c', '--config', dest='config', required=False)
manager.add_command('create_user', CreateUser)
manager.add_command('delete_user', DeleteUser)
manager.add_command('update_image_order', UpdateOrder)
manager.add_command('remove_unused_files', UnusedFiles)

if __name__ == '__main__':
    manager.run()
