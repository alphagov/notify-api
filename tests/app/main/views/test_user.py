from flask import json
from app import db
from app.models import User, Service
from datetime import datetime


def test_should_fetch_users_for_a_service(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get(
        '/service/1234/users',
        headers={
            'Authorization': 'Bearer 1234'
        })
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
        mobile_number="+441234123412",
        password="password",
        active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        password_changed_at=datetime.utcnow(),
        failed_login_count=0,
        role='admin'
    )
    service = Service.query.get(1234)
    service.users.append(user)
    db.session.add(service)
    db.session.commit()

    response = notify_api.test_client().get(
        '/service/1234/users',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert 'users' in data
    assert len(data['users']) == 2
    assert data['users'][0]['emailAddress'] == 'test-user@example.org'
    assert data['users'][1]['emailAddress'] == 'test@test.com'


def test_should_add_user_to_service(notify_api, notify_db, notify_db_session):
    user = User(
        email_address="add-me@test.gov.uk",
        mobile_number="+441234999999",
        password="password",
        active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        password_changed_at=datetime.utcnow(),
        failed_login_count=0,
        role='admin'
    )
    db.session.add(user)
    db.session.commit()

    response = notify_api.test_client().post(
        '/service/1234/add-user',
        data=json.dumps(
            {
                'user': {
                    'emailAddress': 'add-me@test.gov.uk'
                }
            }
        ),
        headers={
            'Authorization': 'Bearer 1234'
        },
        content_type='application/json')
    assert response.status_code == 200

    fetch_response = notify_api.test_client().get(
        '/service/1234/users',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(fetch_response.get_data())
    assert fetch_response.status_code == 200
    assert 'users' in data
    assert len(data['users']) == 2
    assert data['users'][0]['emailAddress'] == 'test-user@example.org'
    assert data['users'][1]['emailAddress'] == 'add-me@test.gov.uk'


def test_cannot_add_user_twice_to_a_service(notify_api, notify_db, notify_db_session):
    user = User(
        email_address="add-me@test.gov.uk",
        mobile_number="+441234999999",
        password="password",
        active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        password_changed_at=datetime.utcnow(),
        failed_login_count=0,
        role='admin'
    )
    db.session.add(user)
    db.session.commit()

    response_1 = notify_api.test_client().post(
        '/service/1234/add-user',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps(
            {
                'user': {
                    'emailAddress': 'add-me@test.gov.uk'
                }
            }
        ),
        content_type='application/json')
    assert response_1.status_code == 200

    response_2 = notify_api.test_client().post(
        '/service/1234/add-user',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps(
            {
                'user': {
                    'emailAddress': 'add-me@test.gov.uk'
                }
            }
        ),
        content_type='application/json')
    assert response_2.status_code == 200

    fetch_response = notify_api.test_client().get(
        '/service/1234/users',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(fetch_response.get_data())
    assert fetch_response.status_code == 200
    assert 'users' in data
    assert len(data['users']) == 2
    assert data['users'][0]['emailAddress'] == 'test-user@example.org'
    assert data['users'][1]['emailAddress'] == 'add-me@test.gov.uk'


def test_user_cannot_be_added_to_non_existant_service(notify_api, notify_db, notify_db_session):
    user = User(
        email_address="add-me@test.gov.uk",
        mobile_number="+441234999999",
        password="password",
        active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        password_changed_at=datetime.utcnow(),
        failed_login_count=0,
        role='admin'
    )
    db.session.add(user)
    db.session.commit()

    response = notify_api.test_client().post(
        '/service/5656/add-user',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps(
            {
                'user': {
                    'emailAddress': 'add-me@test.gov.uk'
                }
            }
        ),
        content_type='application/json')
    assert response.status_code == 404


def test_user_cannot_be_add_non_existant_user_to_service(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().post(
        '/service/1234/add-user',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps(
            {
                'user': {
                    'emailAddress': 'missing@test.gov.uk'
                }
            }
        ),
        content_type='application/json')
    assert response.status_code == 404


def test_should_remove_user_from_a_service(notify_api, notify_db, notify_db_session):
    user = User(
        email_address="add-me@test.gov.uk",
        mobile_number="+441234999999",
        password="password",
        active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        password_changed_at=datetime.utcnow(),
        failed_login_count=0,
        role='admin'
    )
    db.session.add(user)
    db.session.commit()

    post_1 = notify_api.test_client().post(
        '/service/1234/add-user',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps(
            {
                'user': {
                    'emailAddress': 'add-me@test.gov.uk'
                }
            }
        ),
        content_type='application/json')
    assert post_1.status_code == 200

    fetch_1 = notify_api.test_client().get(
        '/service/1234/users',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data_1 = json.loads(fetch_1.get_data())
    assert fetch_1.status_code == 200
    assert len(data_1['users']) == 2

    post_2 = notify_api.test_client().post(
        '/service/1234/remove-user',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps(
            {
                'user': {
                    'emailAddress': 'add-me@test.gov.uk'
                }
            }
        ),
        content_type='application/json')
    assert post_2.status_code == 200

    fetch_2 = notify_api.test_client().get(
        '/service/1234/users',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data_2 = json.loads(fetch_2.get_data())
    assert fetch_2.status_code == 200
    assert 'users' in data_2
    assert len(data_2['users']) == 1
    assert data_2['users'][0]['emailAddress'] == 'test-user@example.org'


def test_user_cannot_be_removed_from_a_non_existent_service(notify_api, notify_db, notify_db_session):
    user = User(
        email_address="add-me@test.gov.uk",
        mobile_number="+441234999999",
        password="password",
        active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        password_changed_at=datetime.utcnow(),
        failed_login_count=0,
        role='admin'
    )
    db.session.add(user)
    db.session.commit()

    response = notify_api.test_client().post(
        '/service/5656/remove-user',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps(
            {
                'user': {
                    'emailAddress': 'add-me@test.gov.uk'
                }
            }
        ),
        content_type='application/json')
    assert response.status_code == 404


def test_user_cannot_be_remove_non_existent_user_from_a_service(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().post(
        '/service/1234/remove-user',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps(
            {
                'user': {
                    'emailAddress': 'missing@test.gov.uk'
                }
            }
        ),
        content_type='application/json')
    assert response.status_code == 404


def test_should_by_404_for_non_numeric_user_id(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get(
        '/users/invalid',
        headers={
            'Authorization': 'Bearer 1234'
        })
    assert response.status_code == 404


def test_should_fetch_user_if_can_find_by_id(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get(
        '/users/1234',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert 'users' in data
    assert data['users']['role'] == 'admin'
    assert data['users']['emailAddress'] == 'test-user@example.org'
    assert not data['users']['locked']
    assert data['users']['active']


def test_should_reject_fetch_user_request_with_no_email(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get(
        '/users',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['error'] == 'No email address provided'


def test_should_fetch_user_if_can_find_by_email(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get(
        '/users?email_address=test-user@example.org',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert 'users' in data
    assert data['users']['role'] == 'admin'
    assert data['users']['emailAddress'] == 'test-user@example.org'
    assert not data['users']['locked']
    assert data['users']['active']
    assert data['users']['failedLoginCount'] == 0


def test_should_only_allow_valid_auth_requests(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().post(
        '/users/auth',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps(
            {
                'userAuthentication': {
                    'password': 'valid-password'
                }
            }
        ),
        content_type='application/json')
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert 'error_details' in data
    assert {'required': ["'emailAddress' is a required property"]} in data['error_details']


def test_should_be_able_to_auth_user(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().post(
        '/users/auth',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps(
            {
                'userAuthentication': {
                    'emailAddress': 'TEST-user@example.org',
                    'password': 'valid-password'
                }
            }
        ),
        content_type='application/json')
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert 'users' in data
    assert data['users']['role'] == 'admin'
    assert data['users']['emailAddress'] == 'test-user@example.org'
    assert not data['users']['locked']
    assert data['users']['active']


def test_should_404_if_user_not_found_on_auth(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().post(
        '/users/auth',
        headers={
            'Authorization': 'Bearer 1234'
        },
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
        headers={
            'Authorization': 'Bearer 1234'
        },
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

    fetch_response = notify_api.test_client().get(
        '/users?email_address=test-user@example.org',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(fetch_response.get_data())
    assert fetch_response.status_code == 200
    assert data['users']['failedLoginCount'] == 1


def test_should_reset_failed_login_count_on_success(notify_api, notify_db, notify_db_session):
    response_1 = notify_api.test_client().post(
        '/users/auth',
        headers={
            'Authorization': 'Bearer 1234'
        },
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

    fetch_response_1 = notify_api.test_client().get(
        '/users?email_address=test-user@example.org',
        headers={
            'Authorization': 'Bearer 1234'
        })

    data = json.loads(fetch_response_1.get_data())
    assert fetch_response_1.status_code == 200
    assert data['users']['failedLoginCount'] == 1

    response_2 = notify_api.test_client().post(
        '/users/auth',
        headers={
            'Authorization': 'Bearer 1234'
        },
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

    fetch_response_2 = notify_api.test_client().get(
        '/users?email_address=test-user@example.org',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(fetch_response_2.get_data())
    assert fetch_response_2.status_code == 200
    assert data['users']['failedLoginCount'] == 0


def test_should_prevent_login_when_too_many_failed_attempts(notify_api, notify_db, notify_db_session):
    for i in range(0, notify_api.config['MAX_FAILED_LOGIN_COUNT'] + 1):
        response = notify_api.test_client().post(
            '/users/auth',
            headers={
                'Authorization': 'Bearer 1234'
            },
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

    fetch_response = notify_api.test_client().get(
        '/users?email_address=test-user@example.org',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(fetch_response.get_data())
    assert fetch_response.status_code == 200
    assert data['users']['failedLoginCount'] == 6
    assert data['users']['locked']

    response_2 = notify_api.test_client().post(
        '/users/auth',
        headers={
            'Authorization': 'Bearer 1234'
        },
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


def test_should_be_able_to_create_users(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().post(
        '/users',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps(
            {
                'user': {
                    'emailAddress': 'TEST-user@example.gov.uk',
                    'mobileNumber': '+449999999999',
                    'password': 'validpassword'
                }
            }
        ),
        content_type='application/json')
    assert response.status_code == 201

    fetch_response = notify_api.test_client().get(
        '/users?email_address=test-user@example.gov.uk',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(fetch_response.get_data())
    assert fetch_response.status_code == 200
    assert not data['users']['active']


def test_should_reject_invalid_user_request(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().post(
        '/users',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps(
            {
                'user': {
                    'emailAddress': 'test-user@example.gov.uk',
                    'password': 'validpassword'
                }
            }
        ),
        content_type='application/json')
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['error'] == 'Invalid JSON'
    assert data['error_details'][0]['required'][0] == "'mobileNumber' is a required property"


def test_should_reject_non_gov_emailst(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().post(
        '/users',
        headers={
            'Authorization': 'Bearer 1234'
        },
        data=json.dumps(
            {
                'user': {
                    'emailAddress': 'test-user@example.com',
                    'mobileNumber': '+449999999999',
                    'password': 'validpassword'
                }
            }
        ),
        content_type='application/json')
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['error'] == 'Invalid JSON'
