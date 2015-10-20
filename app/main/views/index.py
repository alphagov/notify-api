from flask import jsonify, url_for, current_app
from .. import main


@main.route('/')
def index():
    """Entry point for the API, show the resources that are available."""
    return jsonify(links={
        "user.fetch_user_by_id": {
            "url": url_for(
                '.fetch_user_by_id',
                user_id="123",
                _external=True,
                _scheme=current_app.config.get('NOTIFY_HTTP_PROTO', 'http')
            ),
            "method": "GET"
        },
        "user.fetch_user_by_email": {
            "url": url_for(
                '.fetch_user_by_email',
                _external=True,
                _scheme=current_app.config.get('NOTIFY_HTTP_PROTO', 'http')
            ),
            "method": "GET"
        },
        "user.authenticate": {
            "url": url_for(
                '.auth_user',
                _external=True,
                _scheme=current_app.config.get('NOTIFY_HTTP_PROTO', 'http')
            ),
            "method": "POST"
        },
        "notification.create": {
            "url": url_for(
                '.create_sms_notification',
                _external=True,
                _scheme=current_app.config.get('NOTIFY_HTTP_PROTO', 'http')
            ),
            "method": "POST"
        },
        "organisation.fetch": {
            "url": url_for(
                '.fetch_organisation',
                organisation_id="123",
                _external=True,
                _scheme=current_app.config.get('NOTIFY_HTTP_PROTO', 'http')
            ),
            "method": "GET"
        },
        "job.fetch": {
            "url": url_for(
                '.fetch_job',
                job_id="123",
                _external=True,
                _scheme=current_app.config.get('NOTIFY_HTTP_PROTO', 'http')
            ),
            "method": "GET"
        },
        "job.fetch_jobs_by_service": {
            "url": url_for(
                '.fetch_jobs_by_service',
                service_id="123",
                _external=True,
                _scheme=current_app.config.get('NOTIFY_HTTP_PROTO', 'http')
            ),
            "method": "GET"
        },
        "job.create": {
            "url": url_for(
                '.create_job',
                _external=True,
                _scheme=current_app.config.get('NOTIFY_HTTP_PROTO', 'http')
            ),
            "method": "POST"
        },
        "service.fetch_service_by_user_id_and_service_id": {
            "url": url_for(
                '.fetch_service_by_user_id_and_service_id',
                user_id="123",
                service_id="123",
                _external=True,
                _scheme=current_app.config.get('NOTIFY_HTTP_PROTO', 'http')
            ),
            "method": "GET"
        },
        "service.fetch_services_by_user": {
            "url": url_for(
                '.fetch_services_by_user',
                user_id="123",
                _external=True,
                _scheme=current_app.config.get('NOTIFY_HTTP_PROTO', 'http')
            ),
            "method": "GET"
        },
        "service.create": {
            "url": url_for(
                '.create_service',
                _external=True,
                _scheme=current_app.config.get('NOTIFY_HTTP_PROTO', 'http')
            ),
            "method": "POST"
        },
        "notification.fetch": {
            "url": url_for(
                '.fetch_notifications',
                _external=True,
                _scheme=current_app.config.get('NOTIFY_HTTP_PROTO', 'http')
            ),
            "method": "GET"
        },
        "notification.fetch_notifications_by_job": {
            "url": url_for(
                '.fetch_notifications_by_job',
                job_id="123",
                _external=True,
                _scheme=current_app.config.get('NOTIFY_HTTP_PROTO', 'http')
            ),
            "method": "GET"
        }
    }
    ), 200
