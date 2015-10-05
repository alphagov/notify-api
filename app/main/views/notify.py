from flask import jsonify, url_for

from .. import main


@main.route('/')
def index():
    """Entry point for the API, show the resources that are available."""
    return jsonify(links={
        "notification.create": {
            "url": url_for('.create_notification', _external=True),
            "method": "PUT"
        }
    }
    ), 200


@main.route('/notification', methods=['PUT'])
def create_notification():
    return jsonify(
        message="I made a notification"
    )
