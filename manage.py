
from flask.ext.script import Manager
from Paintings.App import create_app
from Paintings.Manager.Users import (CreateUser, DeleteUser)
from Paintings.Manager.InitApp import InitApp
from Paintings.Manager.DbUtils import UpdateOrder

manager = Manager(create_app)
manager.add_option('-c', '--config', dest='config', required=False)
manager.add_command('create_user', CreateUser)
manager.add_command('delete_user', DeleteUser)
manager.add_command('update_image_order', UpdateOrder)
manager.add_command('init', InitApp)

if __name__ == '__main__':
    manager.run()
