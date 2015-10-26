from datetime import datetime
from uuid import uuid4
from flask import jsonify, abort, current_app
from .. import main
from app import db
from app.main.views import get_json_from_request
from app.models import Service, Token, User
from app.main.validators import valid_service_submission
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc, asc


@main.route('/service/<int:service_id>/users', methods=['GET'])
def fetch_users_for_service(service_id):
    users = User.query.filter(
        Service.id == service_id
    ).order_by(asc(User.created_at)).all()

    return jsonify(
        users=[user.serialize() for user in users]
    )


@main.route('/user/<int:user_id>/service/<int:service_id>', methods=['GET'])
def fetch_service_by_user_id_and_service_id(user_id, service_id):
    service = Service.query.filter(
        Service.id == service_id,
        Service.users.any(id=user_id)
    ).first_or_404()

    return jsonify(
        service=service.serialize()
    )


@main.route('/user/<int:user_id>/services', methods=['GET'])
def fetch_services_by_user(user_id):
    services = Service.query.filter(
        Service.users.any(id=user_id)
    ).order_by(desc(Service.created_at)).all()

    return jsonify(
        services=[service.serialize() for service in services]
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

    user = User.query.get(service_from_request['userId'])

    if not user:
        return jsonify(
            error="failed to create service - invalid user"
        ), 400

    try:
        token = Token(token=uuid4())
        db.session.add(token)
        db.session.flush()

        service = Service(
            name=service_from_request['name'],
            created_at=datetime.utcnow(),
            token_id=token.id,
            active=True,
            restricted=True,
            limit=current_app.config['MAX_SERVICE_LIMIT']
        )
        service.users.append(user)
        db.session.add(service)
        db.session.commit()
        return jsonify(
            service=service.serialize()
        ), 201
    except IntegrityError as e:
        print(e.orig)
        db.session.rollback()
        abort(400, "failed to create service")
