from flask import json


def test_should_be_able_to_get_email_job_by_id(notify_api, notify_db, notify_email_db_session, notify_config):
    response = notify_api.test_client().get(
        '/job/1234',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert data['job']['id'] == 1234
    assert data['job']['name'] == 'email job test'


def test_should_return_all_email_jobs_for_a_service(notify_api, notify_db, notify_email_db_session, notify_config):
    create_response = notify_api.test_client().post(
        '/job',
        data=json.dumps(
            {
                'job': {
                    'serviceId': 1234,
                    'name': 'my job'
                }
            }
        ),
        headers={
            'Authorization': 'Bearer 1234'
        },
        content_type='application/json')
    assert create_response.status_code == 201
    response = notify_api.test_client().get(
        '/service/1234/jobs',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert len(data['jobs']) == 2
    assert data['jobs'][0]['name'] == 'my job'
    assert data['jobs'][1]['name'] == 'email job test'


def test_should_be_able_to_get_job_by_id(notify_api, notify_db, notify_db_session, notify_config):
    response = notify_api.test_client().get(
        '/job/1234',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert data['job']['id'] == 1234
    assert data['job']['name'] == 'job test'


def test_should_be_able_to_get_job_by_service_id_id(notify_api, notify_db, notify_db_session, notify_config):
    response = notify_api.test_client().get(
        '/service/1234/jobs',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert len(data['jobs']) == 1
    assert data['jobs'][0]['id'] == 1234
    assert data['jobs'][0]['name'] == 'job test'


def test_should_return_all_jobs_for_a_service(notify_api, notify_db, notify_db_session, notify_config):
    create_response = notify_api.test_client().post(
        '/job',
        data=json.dumps(
            {
                'job': {
                    'serviceId': 1234,
                    'name': 'my job'
                }
            }
        ),
        headers={
            'Authorization': 'Bearer 1234'
        },
        content_type='application/json')
    assert create_response.status_code == 201
    response = notify_api.test_client().get(
        '/service/1234/jobs',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert len(data['jobs']) == 2
    assert data['jobs'][0]['name'] == 'my job'
    assert data['jobs'][1]['name'] == 'job test'


def test_shgould_return_no_jobs_if_none_for_service(notify_api, notify_db, notify_db_session, notify_config):
    response = notify_api.test_client().get(
        '/service/12345/jobs',
        headers={
            'Authorization': 'Bearer 1234'
        })
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert len(data['jobs']) == 0


def test_should_be_a_404_if_job_does_not_exist(notify_api, notify_db_session):
    response = notify_api.test_client().get(
        '/job/12345',
        headers={
            'Authorization': 'Bearer 1234'
        })
    assert response.status_code == 404


def test_should_be_a_404_if_job_id_is_not_an_int(notify_api, notify_db_session):
    response = notify_api.test_client().get(
        '/job/invalid-id',
        headers={
            'Authorization': 'Bearer 1234'
        })
    assert response.status_code == 404


def test_should_be_able_to_create_a_job(notify_api, notify_db_session, notify_config):
    response = notify_api.test_client().post(
        '/job',
        data=json.dumps(
            {
                'job': {
                    'serviceId': 1234,
                    'name': 'my job'
                }
            }
        ),
        headers={
            'Authorization': 'Bearer 1234'
        },
        content_type='application/json')
    data = json.loads(response.get_data())
    assert response.status_code == 201
    assert 'job' in data
    assert 'id' in data['job']


def test_should_be_able_to_create_a_job_with_filename(notify_api, notify_db_session, notify_config):
    response = notify_api.test_client().post(
        '/job',
        data=json.dumps(
            {
                'job': {
                    'serviceId': 1234,
                    'name': 'my job',
                    'filename': 'filename.csv'
                }
            }
        ),
        headers={
            'Authorization': 'Bearer 1234'
        },
        content_type='application/json')
    data = json.loads(response.get_data())
    assert response.status_code == 201
    assert 'job' in data
    assert 'id' in data['job']
    assert 'filename' in data['job']
    assert data['job']['filename'] == 'filename.csv'


def test_should_reject_an_invalid_job(notify_api, notify_db_session, notify_config):
    response = notify_api.test_client().post(
        '/job',
        data=json.dumps(
            {
                'job': {
                    'serviceId': 'not-valid',
                    'name': '1'
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
    assert {'key': 'serviceId', 'message': "'not-valid' is not of type 'integer'"} in data['error_details']
    assert {'key': 'name', 'message': "'1' is too short"} in data['error_details']


def test_should_reject_if_no_job_root_element(notify_api, notify_db_session, notify_config):
    response = notify_api.test_client().post(
        '/job',
        data=json.dumps({}),
        content_type='application/json',
        headers={
            'Authorization': 'Bearer 1234'
        }
    )
    data = json.loads(response.get_data())
    assert data['error'] == "Invalid JSON; must have job as root element"
    assert response.status_code == 400
