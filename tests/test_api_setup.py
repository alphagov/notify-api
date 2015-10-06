import os
from app import create_app
from flask import json


# def test_should_reject_http_traffic_on_production_configuration():
#     app = create_app('live')
#     with app.app_context():
#         client = app.test_client()
#         response = client.get('/')
#         assert response.status_code == 301
#         assert response.location == 'https://localhost/'
#
#
# def test_should_render_production_links_with_https():
#     app = create_app('development')
#     with app.app_context():
#         client = app.test_client()
#         response = client.get('/', headers={'HTTP_X_FORWARDED_PROTO': 'https'})
#         data = json.loads(response.get_data())
#         assert 200 == response.status_code
#         assert data['links']['notification.create']['url'] == "https://localhost/notification"
