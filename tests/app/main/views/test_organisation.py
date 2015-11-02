from flask import json


def test_should_be_able_to_get_organisation_by_id(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get(
        '/organisation/1234',
        headers={
            'Authorization': 'Bearer 1234'
        }
    )
    data = json.loads(response.get_data())
    assert response.status_code == 200
    assert data['organisation']['id'] == 1234
    assert data['organisation']['name'] == 'org test'


def test_should_be_a_404_if_organisation_does_not_exist(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get(
        '/organisation/12345',
        headers={
            'Authorization': 'Bearer 1234'
        }
    )
    assert response.status_code == 404


def test_should_be_a_404_if_organisation_id_is_not_an_int(notify_api, notify_db, notify_db_session):
    response = notify_api.test_client().get(
        '/organisation/invalid-id',
        headers={
            'Authorization': 'Bearer 1234'
        }
    )
    assert response.status_code == 404
