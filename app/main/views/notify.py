from flask import jsonify, url_for, current_app, request, abort
from app.main.validators import valid_sms_notificationb
from .. import main
from uuid import uuid4


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
        }
    }
    ), 200


@main.route('/sms/notification', methods=['POST'])
def create_sms_notification():
    notification = get_json_from_request()

    if not valid_sms_notificationb(notification):
        abort(400, "Invalid JSON; invalid SMS notification")

    return jsonify(
        message="I made a notification",
        id=str(uuid4())
    )


def get_json_from_request():
    if request.content_type not in [
        'application/json',
        'application/json; charset=UTF-8'
    ]:
        abort(400, "Unexpected Content-Type, expecting 'application/json'")
    data = request.get_json()
    if data is None:
        abort(400, "Invalid JSON; must be a valid JSON object")
    if 'notification' not in data:
        abort(400, "Invalid JSON; must have notification as root element")
    return data['notification']
