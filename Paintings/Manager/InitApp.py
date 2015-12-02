""" create database """

from flask.ext.script import Command


class InitApp(Command):
    def run(*args):
        """ create all database tables """
        from ..lib import init_db
        session = init_db.get_db_session()




