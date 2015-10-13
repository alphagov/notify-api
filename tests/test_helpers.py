from flask import json
import re


class BaseApiTest(object):
    pass


class BasePostApiTest(BaseApiTest):
    uuid_regex = re.compile("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")

    path = None

    @staticmethod
    def test_should_reject_if_no_content_type(notify_api):
        response = notify_api.test_client().post(
            '/sms/notification'
        )
        data = json.loads(response.get_data())
        assert data['error'] == "Unexpected Content-Type, expecting \'application/json\'"
        assert response.status_code == 400

    @staticmethod
    def test_should_reject_if_invalid_json(notify_api):
        response = notify_api.test_client().post(
            '/sms/notification',
            data='this is not JSON',
            content_type='application/json'
        )
        data = json.loads(response.get_data())
        assert data['error'] == "The browser (or proxy) sent a request that this server could not understand."
        assert response.status_code == 400

    @staticmethod
    def test_should_reject_if_no_notification_root_element(notify_api):
        response = notify_api.test_client().post(
            '/sms/notification',
            data=json.dumps({}),
            content_type='application/json'
        )
        data = json.loads(response.get_data())
        assert data['error'] == "Invalid JSON; must have notification as root element"
        assert response.status_code == 400
