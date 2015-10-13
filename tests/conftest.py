import pytest
from flask import Flask
import mock
from app import create_app, db
import os
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from alembic.command import upgrade
from alembic.config import Config
from sqlalchemy.schema import MetaData
from config import configs


@pytest.fixture(scope='session')
def notify_api(request):
    print("setting up notify-api")
    app = create_app('test')
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='session')
def notify_db(notify_api, request):
    Migrate(notify_api, db)
    Manager(db, MigrateCommand)
    ALEMBIC_CONFIG = os.path.join(os.path.dirname(__file__), '../migrations/alembic.ini')
    config = Config(ALEMBIC_CONFIG)
    config.set_main_option("script_location", "migrations")
    with notify_api.app_context():
        upgrade(config, 'head')

    def teardown():
        db.session.remove()
        db.drop_all()
        db.engine.execute("drop table alembic_version")
        db.get_engine(notify_api).dispose()

    request.addfinalizer(teardown)


@pytest.fixture(scope='function')
def notify_db_session(request):
    meta = MetaData(bind=db.engine, reflect=True)

    def teardown():
        for tbl in reversed(meta.sorted_tables):
            db.engine.execute(tbl.delete())
    request.addfinalizer(teardown)


@pytest.fixture(scope='function')
def notify_config(notify_api):
    notify_api.config['NOTIFY_API_ENVIRONMENT'] = 'test'
    notify_api.config.from_object(configs['test'])


@pytest.fixture
def app():
    return Flask(__name__)


@pytest.fixture
def os_environ(request):
    env_patch = mock.patch('os.environ', {})
    request.addfinalizer(env_patch.stop)

    return env_patch.start()


@pytest.fixture(autouse=True)
def no_sms(monkeypatch):
    monkeypatch.delattr("app.connectors.sms.clients.TwilioClient.send")
