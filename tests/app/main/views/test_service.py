from flask import json
from . import uuid_regex
from app.models import User, Token
from datetime import datetime
from app import db


def test_should_be_able_to_deactivate_service(notify_api, notify_db, notify_db_session):
    response_1 = notify_api.test_client().get(
        '/user/1234/service/1234',
        headers={
            'Authorization': 'Bearer 1234'
        }
    )
    data = json.loads(response_1.get_data())
    assert data['service']['active']
    response_2 = notify_api.test_client().post(
        '/service/1234/deactivate',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(response_2.get_data())
    assert not data['service']['active']


def test_should_be_able_to_activate_service(notify_api, notify_db, notify_db_session):
    response_1 = notify_api.test_client().post(
        '/service/1234/deactivate',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(response_1.get_data())
    assert not data['service']['active']

    response_2 = notify_api.test_client().post(
        '/service/1234/activate',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(response_2.get_data())
    assert data['service']['active']


def test_should_be_able_to_get_service_by_id_and_user_id(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get(
        '/user/1234/service/1234',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert data['service']['id'] == 1234
    assert data['service']['name'] == 'service test'
    assert data['service']['token']['token'] == '1234'


def test_should_be_able_to_get_service_as_platform_admin(notify_api, notify_db, notify_db_session):
    # Setup a dummy user for tests
    user = User(
        id=9999,
        email_address="test-user@example-2.org",
        mobile_number="+449999123123",
        password='password',
        active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        password_changed_at=datetime.utcnow(),
        role='platform-admin'
    )
    db.session.add(user)
    db.session.commit()

    response = notify_api.test_client().get(
        '/user/9999/service/1234',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert data['service']['id'] == 1234
    assert data['service']['name'] == 'service test'
    assert data['service']['token']['token'] == '1234'


def test_should_be_able_to_get_all_services_for_a_user(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get(
        '/user/1234/services',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert len(data['services']) == 1
    assert data['services'][0]['id'] == 1234
    assert data['services'][0]['name'] == 'service test'


def test_should_be_able_to_get_all_services_as_platform_admin(notify_api, notify_db, notify_db_session):
    # Setup a dummy user for tests
    user = User(
        id=9999,
        email_address="test-user@example-2.org",
        mobile_number="+449999123123",
        password='password',
        active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        password_changed_at=datetime.utcnow(),
        role='platform-admin'
    )
    db.session.add(user)
    db.session.commit()

    response = notify_api.test_client().get(
        '/user/9999/services',
        headers={
            'Authorization': 'Bearer 1234'
        })

    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert len(data['services']) == 1
    assert data['services'][0]['id'] == 1234
    assert data['services'][0]['name'] == 'service test'


def test_should_return_empty_list_if_no_services_for_user(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get(
        '/user/12345/services',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert len(data['services']) == 0


def test_should_be_a_404_of_non_int_org_id(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get(
        '/user/not-valid/services',
        headers={
            'Authorization': 'Bearer 1234'
        })
    assert response.status_code == 404


def test_should_be_able_to_create_a_service(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().post(
        '/service',
        data=json.dumps(
            {
                'service': {
                    'userId': 1234,
                    'name': 'my service'
                }
            }
        ),
        headers={
            'Authorization': 'Bearer 1234'
        },
        content_type='application/json')
    data = json.loads(response.get_data())
    assert response.status_code == 201
    assert 'service' in data
    assert data['service']['name'] == 'my service'
    assert data['service']['active']
    assert data['service']['restricted']
    assert data['service']['limit'] == 100
    assert uuid_regex.match(data['service']['token']['token'])


def test_should_not_be_able_to_create_service_on_client_token(notify_api, notify_db, notify_db_session):
    token = Token(token='client', type='client')
    db.session.add(token)
    db.session.commit()
    response = notify_api.test_client().post(
        '/service',
        data=json.dumps(
            {
                'service': {
                    'userId': 1234,
                    'name': 'my service'
                }
            }
        ),
        headers={
            'Authorization': 'Bearer client'
        },
        content_type='application/json')
    assert response.status_code == 403


def test_should_reject_a_service_with_invalid_user(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().post(
        '/service',
        data=json.dumps(
            {
                'service': {
                    'userId': 9999,
                    'name': 'this is ok'
                }
            }
        ),
        headers={
            'Authorization': 'Bearer 1234'
        },
        content_type='application/json')
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['error'] == 'failed to create service - invalid user'


def test_should_reject_an_invalid_service(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().post(
        '/service',
        data=json.dumps(
            {
                'service': {
                    'name': '1',
                    'userId': 'not-valid'
                }
            }
        ),
        headers={
            'Authorization': 'Bearer 1234'
        },
        content_type='application/json')
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['error'] == 'Invalid JSON'
    assert len(data['error_details']) == 2
    assert {'key': 'userId', 'message': "'not-valid' is not of type 'integer'"} in data['error_details']
    assert {'key': 'name', 'message': "'1' is too short"} in data['error_details']


def test_should_reject_if_no_job_root_element(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().post(
        '/service',
        data=json.dumps({}),
        content_type='application/json',
        headers={
            'Authorization': 'Bearer 1234'
        }
    )
    data = json.loads(response.get_data())
    assert data['error'] == "Invalid JSON; must have service as root element"
    assert response.status_code == 400


def test_should_be_able_to_get_multiple_services_by_user_id(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().post(
        '/service',
        data=json.dumps(
            {
                'service': {
                    'userId': 1234,
                    'name': 'my service'
                }
            }
        ),
        headers={
            'Authorization': 'Bearer 1234'
        },
        content_type='application/json')
    assert response.status_code == 201
    response = notify_api.test_client().get(
        '/user/1234/services',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert len(data['services']) == 2
    assert data['services'][0]['name'] == 'my service'
    assert data['services'][1]['name'] == 'service test'


def test_should_be_a_404_if_service_does_not_exist(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get(
        '/user/1234/service/12345',
        headers={
            'Authorization': 'Bearer 1234'
        })
    assert response.status_code == 404


def test_should_be_a_404_if_service_id_is_not_an_int(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get(
        '/user/1234/service/invalid-id',
        headers={
            'Authorization': 'Bearer 1234'
        })
    assert response.status_code == 404
