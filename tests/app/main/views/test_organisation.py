from flask import json
from tests.test_helpers import BasePostApiTest
from app import db
from app.models import Organisation


class TestFetchingOrganisation(BasePostApiTest):

    def test_should_be_able_to_get_organisation_by_id(self):
        with self.app.app_context():
            db.session.add(Organisation(id=1234, name="test"))
            db.session.commit()
            response = self.client.get('/organisation/1234')
            data = json.loads(response.get_data())
            assert response.status_code == 200
            assert data['organisation']['id'] == 1234
            assert data['organisation']['name'] == 'test'

    def test_should_be_a_404_if_organisation_does_not_exist(self):
        with self.app.app_context():
            response = self.client.get('/organisation/12345')
            assert response.status_code == 404

    def test_should_be_a_404_if_organisation_id_is_not_an_int(self):
        with self.app.app_context():
            response = self.client.get('/organisation/invalid-id')
            assert response.status_code == 404
