import os
from app import create_app
from flask import json
from tests.test_helpers import BaseApiTest


class TestApiSetUp(BaseApiTest):

    @staticmethod
    def test_should_reject_non_https_traffic_on_production_configuration(self):
        app = create_app('live')
        with app.app_context():
            client = app.test_client()
            response = client.get('/')
            assert response.status_code == 301
            assert response.location == 'https://localhost/'

    def test_should_render_production_links_with_https(self):
        self.app.config['NOTIFY_HTTP_PROTO'] = 'https'
        response = self.client.get('/')
        data = json.loads(response.get_data())
        assert 200 == response.status_code
        assert data['links']['notification.create']['url'] == "https://localhost/notification"

    def test_returns_404(self):
        response = self.client.get('/not-found')
        assert 404 == response.status_code

    def test_bearer_token_is_required(self):
        self.do_not_provide_access_token()
        response = self.client.get('/')
        assert 401 == response.status_code
        assert 'WWW-Authenticate' in response.headers

    def test_valid_bearer_token_is_required(self):
        self.do_not_provide_access_token()
        response = self.client.get(
            '/',
            headers={'Authorization': 'Bearer invalid-token'})
        assert 403 == response.status_code

    def test_max_age_is_one_day(self):
        response = self.client.get("/")
        assert 86400 == response.cache_control.max_age
