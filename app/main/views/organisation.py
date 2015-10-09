from flask import jsonify
from .. import main
from app.models import Organisation


@main.route('/organisation/<int:organisation_id>', methods=['GET'])
def fetch_organisation(organisation_id):
    organisation = Organisation.query.filter(Organisation.id == organisation_id).first_or_404()

    return jsonify(
        organisation=organisation.serialize()
    )
