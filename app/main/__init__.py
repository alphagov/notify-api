from flask import Blueprint, current_app, request, redirect

main = Blueprint('main', __name__)

from .views import notify


def check_url_scheme():
    """
    On heroku builds need to ensure that http calls are redirected to https
    """
    print("****** START *********")
    print(request.url)
    print(request.headers)
    print(request.environ)
    print(current_app.config)
    if current_app.config.get('NOTIFY_API_ENVIRONMENT', 'development') == 'live':
        scheme = request.environ.get('HTTP_X_FORWARDED_PROTO', 'http')
        preferred_scheme = current_app.config.get('NOTIFY_HTTP_PROTO', 'http')
        print(scheme)
        print(preferred_scheme)
        if scheme != preferred_scheme:
            print("redirecting")
            print(request.url.replace('http://', 'https://', 1))
            return redirect(request.url.replace('http://', 'https://', 1), code=301)


main.before_request(check_url_scheme)
