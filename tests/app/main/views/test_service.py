from flask import json


def test_should_be_able_to_get_token_by_service_by_id(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get('/service/1234/token')
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert data['token']['id'] == 1234
    assert data['token']['token'] == '1234'


def test_should_return_404_if_no_token_by_service_by_id(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get('/service/12345/token')
    assert response.status_code == 404


def test_should_be_able_to_get_service_by_id(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get('/service/1234')
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert data['service']['id'] == 1234
    assert data['service']['name'] == 'service test'


def test_should_be_able_to_get_service_by_organisation_id(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get('/organisation/1234/services')
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert len(data['services']) == 1
    assert data['services'][0]['id'] == 1234
    assert data['services'][0]['name'] == 'service test'


def test_should_return_empty_list_if_no_services_for_organisation(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get('/organisation/12345/services')
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert len(data['services']) == 0


def test_should_be_a_404_of_non_int_org_id(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get('/organisation/not-valid/services')
    assert response.status_code == 404


def test_should_be_able_to_get_multiple_services_by_organisation_id(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().post(
        '/service',
        data=json.dumps(
            {
                'service': {
                    'organisationId': 1234,
                    'name': 'my service'
                }
            }
        ),
        content_type='application/json')
    assert response.status_code == 201
    response = notify_api.test_client().get('/organisation/1234/services')
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert len(data['services']) == 2
    assert data['services'][0]['name'] == 'my service'
    assert data['services'][1]['name'] == 'service test'


def test_should_be_a_404_if_service_does_not_exist(notify_api):
    response = notify_api.test_client().get('/service/12345')
    assert response.status_code == 404


def test_should_be_a_404_if_service_id_is_not_an_int(notify_api):
    response = notify_api.test_client().get('/service/invalid-id')
    assert response.status_code == 404


def test_should_be_able_to_create_a_service(notify_api, notify_db_session):
    response = notify_api.test_client().post(
        '/service',
        data=json.dumps(
            {
                'service': {
                    'organisationId': 1234,
                    'name': 'my service'
                }
            }
        ),
        content_type='application/json')
    data = json.loads(response.get_data())
    assert response.status_code == 201
    assert 'service' in data
    assert data['service']['active']
    assert data['service']['limit'] == 100


def test_should_reject_a_service_with_invalid_organisation(notify_api):
    response = notify_api.test_client().post(
        '/service',
        data=json.dumps(
            {
                'service': {
                    'organisationId': 999,
                    'name': 'this is ok'
                }
            }
        ),
        content_type='application/json')
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['error'] == 'failed to create service'


def test_should_reject_an_invalid_service(notify_api):
    response = notify_api.test_client().post(
        '/service',
        data=json.dumps(
            {
                'service': {
                    'organisationId': 'not-valid',
                    'name': '1'
                }
            }
        ),
        content_type='application/json')
    data = json.loads(response.get_data())
    assert response.status_code == 400
    assert data['error'] == 'Invalid JSON'
    assert len(data['error_details']) == 2
    assert {'key': 'organisationId', 'message': "'not-valid' is not of type 'integer'"} in data['error_details']
    assert {'key': 'name', 'message': "'1' is too short"} in data['error_details']


def test_should_reject_if_no_job_root_element(notify_api):
    response = notify_api.test_client().post(
        '/service',
        data=json.dumps({}),
        content_type='application/json'
    )
    data = json.loads(response.get_data())
    assert data['error'] == "Invalid JSON; must have service as root element"
    assert response.status_code == 400
