from flask import jsonify, abort
from .. import main
from app import db
from app.main.views import get_json_from_request
from app.models import Job
from app.main.validators import valid_job_submission
from datetime import datetime
from sqlalchemy.exc import IntegrityError


@main.route('/job/<int:job_id>', methods=['GET'])
def fetch_job(job_id):
    job = Job.query.filter(Job.id == job_id).first_or_404()

    return jsonify(
        job=job.serialize()
    )


@main.route('/job', methods=['POST'])
def create_job():
    job_from_request = get_json_from_request('job')

    validation_result, validation_errors = valid_job_submission(job_from_request)
    if not validation_result:
        return jsonify(
            error="Invalid JSON",
            error_details=validation_errors
        ), 400

    job = Job(
        name=job_from_request['name'],
        service_id=job_from_request['serviceId'],
        created_at=datetime.utcnow()
    )
    try:
        db.session.add(job)
        db.session.commit()
        return jsonify(
            job=job.serialize()
        ), 201
    except IntegrityError as e:
        db.session.rollback()
        abort(400, e.orig)
