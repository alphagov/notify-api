from flask import json
import pytest


@pytest.yield_fixture
def post_endpoint_paths():
    cases = [
        '/sms/notification',
        '/job',
        '/service'
    ]
    yield cases


def test_should_reject_if_no_content_type(post_endpoint_paths, notify_api, notify_config):
    for path in post_endpoint_paths:
        response = notify_api.test_client().post(
            path
        )
        data = json.loads(response.get_data())
        assert response.status_code == 400
        assert data['error'] == "Unexpected Content-Type, expecting 'application/json'"


def test_should_reject_if_invalid_json(post_endpoint_paths, notify_api, notify_config):
    for path in post_endpoint_paths:
        response = notify_api.test_client().post(
            path,
            data='this is not JSON',
            content_type='application/json'
        )
        data = json.loads(response.get_data())
        assert response.status_code == 400
        assert data['error'] == "The browser (or proxy) sent a request that this server could not understand."
