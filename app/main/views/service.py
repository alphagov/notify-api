from datetime import datetime
from uuid import uuid4
from flask import jsonify, abort
from .. import main
from app import db
from app.main.views import get_json_from_request
from app.models import Service, Token
from app.main.validators import valid_service_submission
from sqlalchemy.exc import IntegrityError


@main.route('/service/<int:service_id>', methods=['GET'])
def fetch_service(service_id):
    service = Service.query.filter(Service.id == service_id).first_or_404()

    return jsonify(
        service=service.serialize()
    )


@main.route('/service', methods=['POST'])
def create_service():
    service_from_request = get_json_from_request('service')

    validation_result, validation_errors = valid_service_submission(service_from_request)
    if not validation_result:
        return jsonify(
            error="Invalid JSON",
            error_details=validation_errors
        ), 400

    try:
        token = Token(token=uuid4())
        db.session.add(token)
        db.session.flush()

        service = Service(
            name=service_from_request['name'],
            organisations_id=service_from_request['organisationId'],
            created_at=datetime.utcnow(),
            token_id=token.id
        )
        db.session.add(service)
        db.session.commit()
        return jsonify(
            service=service.serialize()
        ), 201
    except IntegrityError as e:
        db.session.rollback()
        abort(400, "failed to create service")
