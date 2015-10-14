from datetime import datetime
from flask import json
from app.models import Job, Service
from app import db, sms_wrapper


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
    service = Service(id=1000, name="unrelated service", created_at=datetime.now(), organisations_id=1234)
    job = Job(id=1000, name="job test", created_at=datetime.now())
    service.job.append(job)
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
                "message": "Some message",
                "jobId": 1000
            }
        }),
        content_type='application/json'
    )

    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['error'] == 'Invalid job id for these credentials'


def test_should_allow_correctly_formed_sms_request(notify_api, notify_db, notify_db_session, notify_config, mocker):
    mocker.patch('app.sms_wrapper.send')
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
    sms_wrapper.send.assert_called_once_with("+441234512345", "hello world", 1)
