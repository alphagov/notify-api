from flask import json
from app.models import Token
from app import db


def test_should_reject_non_https_traffic_on_production_configuration(notify_api, notify_config):
    notify_api.config['NOTIFY_HTTP_PROTO'] = 'https'
    notify_api.config['NOTIFY_API_ENVIRONMENT'] = 'live'
    response = notify_api.test_client().get('/')
    assert response.status_code == 301
    assert response.location == 'https://localhost/'


def test_should_render_production_links_with_https(notify_api, notify_config):
    notify_api.config['NOTIFY_HTTP_PROTO'] = 'https'
    response = notify_api.test_client().get('/')
    data = json.loads(response.get_data())
    assert 200 == response.status_code
    assert data['links']['notification.create']['url'] == "https://localhost/sms/notification"


def test_returns_404(notify_api, notify_config):
    response = notify_api.test_client().get('/not-found')
    assert 404 == response.status_code


def test_bearer_token_is_required(notify_api, notify_config):
    notify_api.config['AUTH_REQUIRED'] = True
    response = notify_api.test_client().get('/')
    assert 401 == response.status_code
    assert 'WWW-Authenticate' in response.headers


def test_valid_bearer_token_is_required(notify_api, notify_db, notify_config):
    notify_api.config['AUTH_REQUIRED'] = True
    response = notify_api.test_client().get(
        '/',
        headers={'Authorization': 'Bearer invalid-token'})
    assert 403 == response.status_code


def test_allow_a_valid_token(notify_api, notify_db, notify_db_session):
    token = Token(id=123, token="token", type='admin')
    db.session.add(token)
    db.session.commit()
    notify_api.config['AUTH_REQUIRED'] = True
    response = notify_api.test_client().get(
        '/',
        headers={'Authorization': 'Bearer token'})
    assert 200 == response.status_code


def test_max_age_is_one_day(notify_api):
    response = notify_api.test_client().get("/")
    assert 86400 == response.cache_control.max_age
