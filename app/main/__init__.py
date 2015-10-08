from flask import Blueprint, current_app, request, redirect, abort

main = Blueprint('main', __name__)

def check_url_scheme():
    """
    On heroku builds need to ensure that http calls are redirected to https
    """
    if current_app.config.get('NOTIFY_API_ENVIRONMENT', 'development') == 'live':
        scheme = request.environ.get('HTTP_X_FORWARDED_PROTO', 'http')
        preferred_scheme = current_app.config.get('NOTIFY_HTTP_PROTO', 'http')
        if scheme != preferred_scheme:
            return redirect(request.url.replace('http://', 'https://', 1), code=301)


def requires_authentication():
    if current_app.config['AUTH_REQUIRED']:
        incoming_token = get_token_from_headers(request.headers)

        if not incoming_token:
            abort(401)
        if not token_is_valid(incoming_token):
            abort(403, incoming_token)


def token_is_valid(incoming_token):
    return encryption.checkpw(incoming_token, current_app.config.get("API_TOKEN"))


def get_token_from_headers(headers):
    auth_header = headers.get('Authorization', '')
    if auth_header[:7] != 'Bearer ':
        return None
    return auth_header[7:]


main.before_request(check_url_scheme)
main.before_request(requires_authentication)


@main.after_request
def add_cache_control(response):
    response.cache_control.max_age = 24 * 60 * 60
    return response


from .views import notify
from . import errors, encryption
