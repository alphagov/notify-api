from flask import json
from .test_helpers import BasePostApiTest


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
        assert data['message'] == 'I made a notification'
        assert self.uuid_regex.match(data['id']), data['id']

    def test_should_reject_incorrectly_formed_sms_request(self):
        response = self.client.post(
            '/sms/notification',
            data=json.dumps({
                "notification": {
                    "to": "someone",
                    "message": "hello world"
                }
            }),
            content_type='application/json'
        )
        data = json.loads(response.get_data())
        assert response.status_code == 400
        assert data['error'] == 'Invalid JSON; invalid SMS notification'
