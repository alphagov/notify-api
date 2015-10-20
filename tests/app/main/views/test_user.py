from flask import json
from app import db
from app.models import User, Service
from datetime import datetime


def test_should_fetch_users_for_a_service(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get('/service/1234/users')
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert 'users' in data
    assert len(data['users']) == 1
    assert data['users'][0]['role'] == 'admin'
    assert data['users'][0]['emailAddress'] == 'test-user@example.org'
    assert not data['users'][0]['locked']
    assert data['users'][0]['active']
    assert data['users'][0]['failedLoginCount'] == 0


def test_should_fetch_all_users_for_a_service(notify_api, notify_db, notify_db_session):
    user = User(
        email_address="test@test.com",
        password="password",
        active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        password_changed_at=datetime.utcnow(),
        failed_login_count=0,
        role='admin',
        organisation_id=1234
    )
    service = Service.query.get(1234)
    service.users.append(user)
    db.session.add(service)
    db.session.commit()

    response = notify_api.test_client().get('/service/1234/users')
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert 'users' in data
    assert len(data['users']) == 2
    assert data['users'][0]['emailAddress'] == 'test-user@example.org'
    assert data['users'][1]['emailAddress'] == 'test@test.com'


def test_should_by_404_for_non_numeric_user_id(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get('/users/invalid')
    assert response.status_code == 404


def test_should_fetch_user_if_can_find_by_id(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get('/users/1234')
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert 'users' in data
    assert data['users']['organisationId'] == 1234
    assert data['users']['role'] == 'admin'
    assert data['users']['emailAddress'] == 'test-user@example.org'
    assert not data['users']['locked']
    assert data['users']['active']
    assert data['users']['failedLoginCount'] == 0


def test_should_reject_fetch_user_request_with_no_email(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get('/users')
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['error'] == 'No email address provided'


def test_should_fetch_user_if_can_find_by_email(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get('/users?email_address=test-user@example.org')
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert 'users' in data
    assert data['users']['organisationId'] == 1234
    assert data['users']['role'] == 'admin'
    assert data['users']['emailAddress'] == 'test-user@example.org'
    assert not data['users']['locked']
    assert data['users']['active']
    assert data['users']['failedLoginCount'] == 0


def test_should_only_allow_valid_auth_requests(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().post(
        '/users/auth',
        data=json.dumps(
            {
                'userAuthentication': {
                    'password': 'valid-password'
                }
            }
        ),
        content_type='application/json')
    data = json.loads(response.get_data())
    print(data)
    assert response.status_code == 400
    assert 'error_details' in data
    assert {'required': ["'emailAddress' is a required property"]} in data['error_details']


def test_should_be_able_to_auth_user(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().post(
        '/users/auth',
        data=json.dumps(
            {
                'userAuthentication': {
                    'emailAddress': 'test-user@example.org',
                    'password': 'valid-password'
                }
            }
        ),
        content_type='application/json')
    data = json.loads(response.get_data())
    print(data)
    assert response.status_code == 200
    assert 'users' in data
    assert data['users']['organisationId'] == 1234
    assert data['users']['role'] == 'admin'
    assert data['users']['emailAddress'] == 'test-user@example.org'
    assert not data['users']['locked']
    assert data['users']['active']


def test_should_404_if_user_not_found_on_auth(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().post(
        '/users/auth',
        data=json.dumps(
            {
                'userAuthentication': {
                    'emailAddress': 'test-user123@example.org',
                    'password': 'valid-password'
                }
            }
        ),
        content_type='application/json')
    assert response.status_code == 404


def test_should_increment_failed_login_count(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().post(
        '/users/auth',
        data=json.dumps(
            {
                'userAuthentication': {
                    'emailAddress': 'test-user@example.org',
                    'password': 'invalid-password'
                }
            }
        ),
        content_type='application/json')
    assert response.status_code == 403

    fetch_response = notify_api.test_client().get('/users?email_address=test-user@example.org')
    data = json.loads(fetch_response.get_data())
    assert fetch_response.status_code == 200
    assert data['users']['failedLoginCount'] == 1


def test_should_reset_failed_login_count_on_success(notify_api, notify_db, notify_db_session):
    response_1 = notify_api.test_client().post(
        '/users/auth',
        data=json.dumps(
            {
                'userAuthentication': {
                    'emailAddress': 'test-user@example.org',
                    'password': 'invalid-password'
                }
            }
        ),
        content_type='application/json')
    assert response_1.status_code == 403

    fetch_response_1 = notify_api.test_client().get('/users?email_address=test-user@example.org')
    data = json.loads(fetch_response_1.get_data())
    assert fetch_response_1.status_code == 200
    assert data['users']['failedLoginCount'] == 1

    response_2 = notify_api.test_client().post(
        '/users/auth',
        data=json.dumps(
            {
                'userAuthentication': {
                    'emailAddress': 'test-user@example.org',
                    'password': 'valid-password'
                }
            }
        ),
        content_type='application/json')
    assert response_2.status_code == 200

    fetch_response_2 = notify_api.test_client().get('/users?email_address=test-user@example.org')
    data = json.loads(fetch_response_2.get_data())
    assert fetch_response_2.status_code == 200
    assert data['users']['failedLoginCount'] == 0


def test_should_prevent_login_when_too_many_failed_attempts(notify_api, notify_db, notify_db_session):
    for i in range(0, notify_api.config['MAX_FAILED_LOGIN_COUNT'] + 1):
        response = notify_api.test_client().post(
            '/users/auth',
            data=json.dumps(
                {
                    'userAuthentication': {
                        'emailAddress': 'test-user@example.org',
                        'password': 'invalid-password'
                    }
                }
            ),
            content_type='application/json')
        assert response.status_code == 403

    fetch_response = notify_api.test_client().get('/users?email_address=test-user@example.org')
    data = json.loads(fetch_response.get_data())
    assert fetch_response.status_code == 200
    assert data['users']['failedLoginCount'] == 6
    assert data['users']['locked']

    response_2 = notify_api.test_client().post(
        '/users/auth',
        data=json.dumps(
            {
                'userAuthentication': {
                    'emailAddress': 'test-user@example.org',
                    'password': 'valid-password'
                }
            }
        ),
        content_type='application/json')
    assert response_2.status_code == 403
