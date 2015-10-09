import os
from app import create_app, db
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from alembic.command import upgrade
from alembic.config import Config


def setup_module():
    app = create_app('test')
    Migrate(app, db)
    Manager(db, MigrateCommand)
    ALEMBIC_CONFIG = os.path.join(os.path.dirname(__file__), '../migrations/alembic.ini')
    config = Config(ALEMBIC_CONFIG)
    config.set_main_option(
        "script_location",
        "migrations")
    with app.app_context():
        upgrade(config, 'head')
    print("Done db setup")


def teardown_module():
    app = create_app('test')
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.execute("drop table alembic_version")
        db.get_engine(app).dispose()
