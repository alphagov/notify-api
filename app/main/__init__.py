from flask import Blueprint, current_app, request, redirect

main = Blueprint('main', __name__)

from .views import notify


def check_url_scheme():
    """
    On heroku builds need to ensure that http calls are redirected to https
    """
    if current_app.config.get('NOTIFY_API_ENVIRONMENT', 'development') == 'live':
        scheme = request.environ.get('werkzeug.proxy_fix.orig_wsgi_url_scheme', 'http')
        preferred_scheme = current_app.config.get('NOTIFY_HTTP_PROTO', 'http')
        print(scheme)
        print(preferred_scheme)
        if scheme != preferred_scheme:
            return redirect(request.url.replace('http://', 'https://', 1), code=301)


main.before_request(check_url_scheme)
