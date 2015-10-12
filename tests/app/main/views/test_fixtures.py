from flask import json
from app.models import Organisation
from app import db
#
# def test_1(notify_api):
#     response = notify_api.test_client().post(
#         '/sms/notification',
#         data=json.dumps({
#             "notification": {
#                 "to": "+441234512345",
#                 "message": "hello world"
#             }
#         }),
#         content_type='application/json'
#     )
#     assert response.status_code == 200
#
#


def test_2(notify_api, notify_db, notify_db_session):
    org = Organisation(id=123, name="test_2")
    db.session.add(org)
    db.session.commit()
    from time import sleep
    sleep(10)
    response = notify_api.test_client().post(
        '/sms/notification',
        data=json.dumps({
            "notification": {
                "to": "+441234512345",
                "message": "hello world"
            }
        }),
        content_type='application/json'
    )
    assert response.status_code == 200


def test_3(notify_api, notify_db, notify_db_session):
    org = Organisation(id=123, name="test_3")
    db.session.add(org)
    db.session.commit()
    from time import sleep
    sleep(10)
    response = notify_api.test_client().post(
        '/sms/notification',
        data=json.dumps({
            "notification": {
                "to": "+441234512345",
                "message": "hello world"
            }
        }),
        content_type='application/json'
    )
    assert response.status_code == 200
