from flask import json
from tests.test_helpers import BasePostApiTest


class TestSendingSmsNotification(BasePostApiTest):

    path = "/sms/notification"

    def test_should_allow_correctly_formed_sms_request(self):
        response = self.client.post(
            '/sms/notification',
            data=json.dumps({
                "notification": {
                    "to": "+441234512345",
                    "message": "hello world"
                }
            }),
            content_type='application/json'
        )
        data = json.loads(response.get_data())
        assert response.status_code == 200
        assert self.uuid_regex.match(data['id']), data['id']

    def test_should_reject_incorrectly_formed_sms_request(self):
        response = self.client.post(
            '/sms/notification',
            data=json.dumps({
                "notification": {
                    "to": "someone",
                    "message": ""
                }
            }),
            content_type='application/json'
        )
        data = json.loads(response.get_data())
        assert response.status_code == 400
        assert data['error'] == 'Invalid JSON'
        assert len(data['error_details']) == 2
        assert data['error_details'][0]['key'] == 'message'
        assert data['error_details'][0]['message'] == "'' is too short"
        assert data['error_details'][1]['key'] == 'to'
        assert data['error_details'][1]['message'] == "'someone' does not match '^\\\+44[\\\d]{10}$'"

    def test_should_reject_missing_data_on_sms_request(self):
        response = self.client.post(
            '/sms/notification',
            data=json.dumps({
                "notification": {
                }
            }),
            content_type='application/json'
        )
        data = json.loads(response.get_data())
        assert response.status_code == 400
        assert data['error'] == 'Invalid JSON'
        assert len(data['error_details']) == 1
        print(data)
        assert data['error_details'][0]['required'] == ["'to' is a required property", "'message' is a required property"]  # noqa
