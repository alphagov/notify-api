from flask import jsonify
from .. import main
from app.models import Service


@main.route('/service/<int:service_id>', methods=['GET'])
def fetch_service(service_id):
    service = Service.query.filter(Service.id == service_id).first_or_404()

    return jsonify(
        service=service.serialize()
    )
