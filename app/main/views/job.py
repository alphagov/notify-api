from flask import jsonify
from .. import main
from app.models import Job


@main.route('/job/<int:job_id>', methods=['GET'])
def fetch_job(job_id):
    job = Job.query.filter(Job.id == job_id).first_or_404()

    return jsonify(
        job=job.serialize()
    )
