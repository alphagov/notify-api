from app import create_app
import os


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
        self.app = create_app('test')
        self.client = self.app.test_client()
        self.setup_authorization()

    def setup_authorization(self):
        """Set up bearer token and pass on all requests"""
        valid_token = 'valid-token'
        self.app.wsgi_app = WSGIApplicationWithEnvironment(
            self.app.wsgi_app,
            HTTP_AUTHORIZATION='Bearer {}'.format(valid_token))

    def do_not_provide_access_token(self):
        self.app.wsgi_app = self.app.wsgi_app.app
