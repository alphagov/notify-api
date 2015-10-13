from app import db
from app.models import Organisation, Service, Job
from datetime import datetime
from flask import json


def test_should_be_able_to_get_job_by_id(notify_api, notify_db, notify_db_session):
    org = Organisation(id=1234, name="org test")
    service = Service(id=1234, name="service test", created_at=datetime.now())
    job = Job(id=1234, name="job test", created_at=datetime.now())
    service.job.append(job)
    org.service.append(service)
    db.session.add(org)
    db.session.commit()

    response = notify_api.test_client().get('/job/1234')
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert data['job']['id'] == 1234
    assert data['job']['name'] == 'job test'


def test_should_be_a_404_if_job_does_not_exist(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get('/job/12345')
    assert response.status_code == 404


def test_should_be_a_404_if_job_id_is_not_an_int(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get('/job/invalid-id')
    assert response.status_code == 404
