from datetime import datetime
from flask import json
from app.models import Job, Service, Token, User, Usage
from app import db


def test_should_reject_incorrectly_formed_sms_request(notify_api, notify_config):
    response = notify_api.test_client().post(
        '/sms/notification',
        data=json.dumps({
            "notification": {
                "to": "someone",
                "message": ""
            }
        }),
        content_type='application/json'
    )
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['error'] == 'Invalid JSON'
    assert len(data['error_details']) == 2
    assert data['error_details'][0]['key'] == 'message'
    assert data['error_details'][0]['message'] == "'' is too short"
    assert data['error_details'][1]['key'] == 'to'
    assert data['error_details'][1]['message'] == "'someone' does not match '^\\\+44[\\\d]{10}$'"


def test_should_reject_missing_data_on_sms_request(notify_api, notify_config):
    response = notify_api.test_client().post(
        '/sms/notification',
        data=json.dumps({
            "notification": {
            }
        }),
        content_type='application/json'
    )
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['error'] == 'Invalid JSON'
    assert len(data['error_details']) == 1
    assert data['error_details'][0]['required'] == ["'to' is a required property",
                                                    "'message' is a required property"]  # noqa


def test_should_reject_request_if_kill_switch_enabled(notify_api, notify_config):
    notify_api.config['SMS_ENABLED'] = False
    response = notify_api.test_client().post(
        '/sms/notification',
        data=json.dumps({
            "notification": {
                "to": "+441234512345",
                "message": "hello world"
            }
        }),
        content_type='application/json'
    )
    data = json.loads(response.get_data())
    assert data['error'] == 'SMS is unavailable'
    assert response.status_code == 503


def test_should_reject_notification_if_invalid_token(notify_api, notify_db, notify_db_session, notify_config):
    response = notify_api.test_client().post(
        '/sms/notification',
        headers={
            'Authorization': 'Bearer does-not-exist'
        },
        data=json.dumps({
            "notification": {
                "to": "+441234512345",
                "message": "Some message"
            }
        }),
        content_type='application/json'
    )

    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['error'] == 'No service associated with these credentials'


def test_should_reject_notification_if_no_token(notify_api, notify_db, notify_db_session, notify_config):
    response = notify_api.test_client().post(
        '/sms/notification',
        data=json.dumps({
            "notification": {
                "to": "+441234512345",
                "message": "Some message"
            }
        }),
        content_type='application/json'
    )

    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['error'] == 'No credentials supplied'


def test_should_reject_notification_if_service_is_inactive(notify_api, notify_db, notify_db_session, notify_config):
    service = Service.query.get(1234)
    service.active = False
    db.session.add(service)
    db.session.commit()

    response = notify_api.test_client().post(
        '/sms/notification',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps({
            "notification": {
                "to": "+441234512345",
                "message": "Some message"
            }
        }),
        content_type='application/json'
    )

    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['error'] == 'Service is inactive'


def test_should_reject_notification_if_invalid_job_id(notify_api, notify_db, notify_db_session, notify_config):
    response = notify_api.test_client().post(
        '/sms/notification',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps({
            "notification": {
                "to": "+441234512345",
                "message": "Some message",
                "jobId": 999
            }
        }),
        content_type='application/json'
    )

    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['error'] == 'No job associated with this job id'


def test_should_reject_notification_if_job_id_not_on_service(notify_api, notify_db, notify_db_session, notify_config):
    service = Service(
        id=1000,
        name="unrelated service",
        created_at=datetime.now(),
        active=True,
        restricted=True,
        limit=100
    )
    job = Job(id=1000, name="job test", created_at=datetime.now())
    job.service = service
    db.session.add(service)
    db.session.add(job)
    db.session.commit()
    response = notify_api.test_client().post(
        '/sms/notification',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps({
            "notification": {
                "to": "+441234512345",
                "message": "Some message",
                "jobId": 1000
            }
        }),
        content_type='application/json'
    )

    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['error'] == 'Invalid job id for these credentials'


def test_should_allow_correctly_formed_sms_request(notify_api, notify_db, notify_db_session, notify_config):
    response = notify_api.test_client().post(
        '/sms/notification',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps({
            "notification": {
                "to": "+441234512345",
                "message": "hello world"
            }
        }),
        content_type='application/json'
    )
    data = json.loads(response.get_data())
    assert response.status_code == 201
    assert 'notification' in data
    assert data['notification']['message'] == "hello world"
    assert data['notification']['method'] == "sms"
    assert data['notification']['status'] == "created"
    assert data['notification']['jobId']


def test_records_new_usage(notify_api, notify_db, notify_db_session, notify_config):
    current_usage = Usage.query.filter(Usage.service_id == 1234).all()
    assert len(current_usage) == 0

    response = notify_api.test_client().post(
        '/sms/notification',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps({
            "notification": {
                "to": "+441234512345",
                "message": "hello world"
            }
        }),
        content_type='application/json'
    )
    assert response.status_code == 201
    new_usage = Usage.query.filter(Usage.service_id == 1234).all()
    assert len(new_usage) == 1
    assert new_usage[0].count == 1


def test_records_new_usage_on_the_same_day(notify_api, notify_db, notify_db_session, notify_config):
    current_usage = Usage.query.filter(Usage.service_id == 1234).all()
    assert len(current_usage) == 0

    notify_api.test_client().post(
        '/sms/notification',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps({
            "notification": {
                "to": "+441234512345",
                "message": "hello world"
            }
        }),
        content_type='application/json'
    )
    new_usage = Usage.query.filter(Usage.service_id == 1234).all()
    assert len(new_usage) == 1
    assert new_usage[0].count == 1

    notify_api.test_client().post(
        '/sms/notification',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps({
            "notification": {
                "to": "+441234512345",
                "message": "hello world"
            }
        }),
        content_type='application/json'
    )

    new_usage = Usage.query.filter(Usage.service_id == 1234).all()
    assert len(new_usage) == 1
    assert new_usage[0].count == 2


def test_should_reject_notification_if_over_limit(notify_api, notify_db, notify_db_session, notify_config):
    service = Service.query.filter(Service.id == 1234).first()
    service.limit = 1
    db.session.add(service)
    db.session.commit()

    response_1 = notify_api.test_client().post(
        '/sms/notification',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps({
            "notification": {
                "to": "+441234512345",
                "message": "hello world"
            }
        }),
        content_type='application/json'
    )
    assert response_1.status_code == 201
    new_usage = Usage.query.filter(Usage.service_id == 1234).all()
    assert len(new_usage) == 1
    assert new_usage[0].count == 1

    response_2 = notify_api.test_client().post(
        '/sms/notification',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps({
            "notification": {
                "to": "+441234512345",
                "message": "hello world"
            }
        }),
        content_type='application/json'
    )
    assert response_2.status_code == 429
    data = json.loads(response_2.get_data())
    assert data['error'] == 'Exceeded sending limits for today'


def test_should_permit_allowed_numbers_on_restricted_service(notify_api, notify_db, notify_db_session, notify_config):
    user = User.query.get(1234)
    token = Token(id=1000, token="restricted")
    service = Service(
        id=1000,
        name='restricted',
        restricted=True,
        active=True,
        limit=100,
        created_at=datetime.utcnow(),
        token=token
    )
    service.users.append(user)
    db.session.add(token)
    db.session.add(service)
    db.session.commit()

    response = notify_api.test_client().post(
        '/sms/notification',
        headers={
            'Authorization': 'Bearer restricted'
        },
        data=json.dumps({
            "notification": {
                "to": "+449999234234",
                "message": "hello world"
            }
        }),
        content_type='application/json'
    )
    data = json.loads(response.get_data())
    print(data)
    assert response.status_code == 201
    assert 'notification' in data
    assert data['notification']['message'] == "hello world"
    assert data['notification']['method'] == "sms"
    assert data['notification']['status'] == "created"
    assert data['notification']['jobId']


def test_should_limit_users_on_restricted_service(notify_api, notify_db, notify_db_session, notify_config):
    user = User.query.get(1234)
    token = Token(id=1000, token="restricted")
    service = Service(
        id=1000,
        name='restricted',
        restricted=True,
        active=True,
        limit=100,
        created_at=datetime.utcnow(),
        token=token
    )
    service.users.append(user)
    db.session.add(token)
    db.session.add(service)
    db.session.commit()

    response = notify_api.test_client().post(
        '/sms/notification',
        headers={
            'Authorization': 'Bearer restricted'
        },
        data=json.dumps({
            "notification": {
                "to": "+441234512345",
                "message": "hello world"
            }
        }),
        content_type='application/json'
    )
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['error'] == 'Restricted service: cannot send notification to this number'


def test_should_have_correct_service_id_on_new_job(notify_api, notify_db, notify_db_session, notify_config):
    response = notify_api.test_client().post(
        '/sms/notification',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps({
            "notification": {
                "to": "+441234512345",
                "message": "hello world"
            }
        }),
        content_type='application/json'
    )
    data = json.loads(response.get_data())
    assert response.status_code == 201

    job_response = notify_api.test_client().get('/job/{}'.format(data['notification']['jobId']))
    job_data = json.loads(job_response.get_data())
    assert 'job' in job_data
    assert job_data['job']['serviceId'] == 1234


def test_should_use_existing_job_if_supplied(notify_api, notify_db, notify_db_session, notify_config):
    response = notify_api.test_client().post(
        '/sms/notification',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps({
            "notification": {
                "to": "+441234512345",
                "message": "hello world",
                "jobId": 1234
            }
        }),
        content_type='application/json'
    )
    data = json.loads(response.get_data())
    assert response.status_code == 201
    assert 'notification' in data
    assert data['notification']['jobId'] == 1234


def test_should_have_correct_service_id_on_existing_job(notify_api, notify_db, notify_db_session, notify_config):
    response = notify_api.test_client().post(
        '/sms/notification',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps({
            "notification": {
                "to": "+441234512345",
                "message": "hello world",
                "jobId": 1234
            }
        }),
        content_type='application/json'
    )
    data = json.loads(response.get_data())
    assert response.status_code == 201

    job_response = notify_api.test_client().get('/job/{}'.format(data['notification']['jobId']))
    job_data = json.loads(job_response.get_data())
    assert 'job' in job_data
    assert job_data['job']['serviceId'] == 1234


def test_should_create_job_if_no_job_id_supplied(notify_api, notify_db, notify_db_session, notify_config):
    response = notify_api.test_client().post(
        '/sms/notification',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps({
            "notification": {
                "to": "+441234512345",
                "message": "hello world"
            }
        }),
        content_type='application/json'
    )
    data = json.loads(response.get_data())
    assert response.status_code == 201
    assert 'notification' in data
    job_response = notify_api.test_client().get(
        '/job/{}'.format(data['notification']['jobId']),
        headers={
            'Authorization': 'Bearer 1234'
        },
    )
    assert job_response.status_code == 200
    job_data = json.loads(job_response.get_data())
    assert job_data['job']['name'] == 'Autogenerated'


def test_should_fetch_notification_by_job_id(notify_api, notify_db, notify_db_session, notify_config):
    response = notify_api.test_client().get("/job/1234/notifications")
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert len(data['notifications']) == 1
    assert data['notifications'][0]['method'] == 'sms'
    assert data['notifications'][0]['to'] == 'phone-number'
    assert data['notifications'][0]['message'] == 'this is a message'


def test_should_fetch_all_notifications_by_job_id(notify_api, notify_db, notify_db_session, notify_config):
    response = notify_api.test_client().post(
        '/sms/notification',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps({
            "notification": {
                "to": "+441234512345",
                "message": "hello world",
                "jobId": 1234
            }
        }),
        content_type='application/json'
    )
    assert response.status_code == 201

    response = notify_api.test_client().get("/job/1234/notifications")
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert len(data['notifications']) == 2
    assert data['notifications'][0]['message'] == 'hello world'
    assert data['notifications'][1]['message'] == 'this is a message'
