from flask import json
from tests.test_helpers import BasePostApiTest
from app import db
from app.models import Organisation, Service
from datetime import datetime


class TestFetchingService(BasePostApiTest):

    def test_should_be_able_to_get_organisation_by_id(self):
        with self.app.app_context():
            org = Organisation(id=1234, name="org test")
            service = Service(id=1234, name="service test", token="1234", organisation=org, created_at=datetime.now())
            db.session.add(org)
            db.session.add(service)
            db.session.commit()

            response = self.client.get('/service/1234')
            data = json.loads(response.get_data())
            assert response.status_code == 200
            assert data['service']['id'] == 1234
            assert data['service']['name'] == 'service test'
            assert data['service']['organisation']['name'] == 'org test'

    def test_should_be_a_404_if_organisation_does_not_exist(self):
        with self.app.app_context():
            response = self.client.get('/service/12345')
            assert response.status_code == 404

    def test_should_be_a_404_if_organisation_id_is_not_an_int(self):
        with self.app.app_context():
            response = self.client.get('/service/invalid-id')
            assert response.status_code == 404
