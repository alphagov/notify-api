from flask import jsonify
from .. import main
from app.models import Organisation
from app.main.auth.token_auth import token_type_required


@main.route('/organisation/<int:organisation_id>', methods=['GET'])
@token_type_required('admin')
def fetch_organisation(organisation_id):
    organisation = Organisation.query.filter(Organisation.id == organisation_id).first_or_404()

    return jsonify(
        organisation=organisation.serialize()
    )
