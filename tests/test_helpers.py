from flask import json
import re
import os
from app import create_app
from . import setup_module, teardown_module


class WSGIApplicationWithEnvironment(object):
    def __init__(self, app, **kwargs):
        self.app = app
        self.kwargs = kwargs

    def __call__(self, environ, start_response):
        for key, value in self.kwargs.items():
            environ[key] = value
        return self.app(environ, start_response)


class BaseApiTest(object):

    def setup(self):
        os.environ['TWILIO_ACCOUNT_SID'] = 'TEST'
        os.environ['TWILIO_AUTH_TOKEN'] = 'TEST'
        os.environ['TWILIO_NUMBER'] = 'TEST'
        self.app = create_app('test')
        self.client = self.app.test_client()
        self.setup_authorization()

    @classmethod
    def setup_class(cls):
        setup_module()

    @classmethod
    def teardown_class(cls):
        teardown_module()

    def setup_authorization(self):
        """Set up bearer token and pass on all requests"""
        valid_token = 'valid-token'
        self.app.wsgi_app = WSGIApplicationWithEnvironment(
            self.app.wsgi_app,
            HTTP_AUTHORIZATION='Bearer {}'.format(valid_token))

    def do_not_provide_access_token(self):
        self.app.wsgi_app = self.app.wsgi_app.app


class BasePostApiTest(BaseApiTest):
    uuid_regex = re.compile("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")

    path = None

    def test_should_reject_if_no_content_type(self):
        response = self.client.post(
            '/sms/notification'
        )
        data = json.loads(response.get_data())
        assert data['error'] == "Unexpected Content-Type, expecting \'application/json\'"
        assert response.status_code == 400

    def test_should_reject_if_invalid_json(self):
        response = self.client.post(
            '/sms/notification',
            data='this is not JSON',
            content_type='application/json'
        )
        data = json.loads(response.get_data())
        assert data['error'] == "The browser (or proxy) sent a request that this server could not understand."
        assert response.status_code == 400

    def test_should_reject_if_no_notification_root_element(self):
        response = self.client.post(
            '/sms/notification',
            data=json.dumps({}),
            content_type='application/json'
        )
        data = json.loads(response.get_data())
        assert data['error'] == "Invalid JSON; must have notification as root element"
        assert response.status_code == 400
