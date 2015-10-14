from flask import jsonify, url_for, current_app
from .. import main


@main.route('/')
def index():
    """Entry point for the API, show the resources that are available."""
    return jsonify(links={
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
        "job.create": {
            "url": url_for(
                '.create_job',
                _external=True,
                _scheme=current_app.config.get('NOTIFY_HTTP_PROTO', 'http')
            ),
            "method": "POST"
        },
        "service.fetch": {
            "url": url_for(
                '.fetch_service',
                service_id="123",
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
        }
    }
    ), 200
