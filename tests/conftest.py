import pytest
from datetime import datetime
import mock
from app import create_app, db
import os
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from alembic.command import upgrade
from alembic.config import Config
from sqlalchemy.schema import MetaData
from app.models import Organisation, Service, Job, Token, User, Notification
from config import configs
from app.main.encryption import generate_password_hash


@pytest.fixture(scope='session')
def notify_api(request):
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
    def teardown():
        for tbl in reversed(meta.sorted_tables):
            db.engine.execute(tbl.delete())

    meta = MetaData(bind=db.engine, reflect=True)
    teardown()
    # Set up dummy org, with a service and a job
    org = Organisation(id=1234, name="org test")
    token = Token(id=1234, token="1234")
    service = Service(id=1234, name="service test", created_at=datetime.utcnow(), token=token, organisation=org)
    job = Job(id=1234, name="job test", created_at=datetime.utcnow(), service=service)
    notification = Notification(
        id=1234,
        to="phone-number",
        message="this is a message",
        job=job,
        status="created",
        method="sms",
        created_at=datetime.utcnow()
    )

    # Setup a dummy user for tests
    user = User(
        id=1234,
        email_address="test-user@example.org",
        password=generate_password_hash('valid-password'),
        active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        password_changed_at=datetime.utcnow(),
        role='admin',
        organisation=org
    )

    db.session.add(token)
    db.session.add(org)
    db.session.add(service)
    db.session.add(notification)
    db.session.add(job)
    db.session.add(user)
    db.session.commit()

    request.addfinalizer(teardown)


@pytest.fixture(scope='function')
def notify_config(notify_api):
    notify_api.config['NOTIFY_API_ENVIRONMENT'] = 'test'
    notify_api.config.from_object(configs['test'])


@pytest.fixture
def os_environ(request):
    env_patch = mock.patch('os.environ', {})
    request.addfinalizer(env_patch.stop)

    return env_patch.start()


@pytest.fixture(autouse=True)
def no_sms(monkeypatch):
    monkeypatch.delattr("app.connectors.sms.clients.TwilioClient.send")
