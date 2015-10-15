from app.main.validators import valid_sms_notification, valid_job_submission, \
    valid_service_submission, valid_user_authentication_submission
import pytest

message = {
    "to": "+447827992607",
    "message": "This is a message"
}


@pytest.yield_fixture
def sms_test_cases():
    cases = [
        (
            {
                "to": "+447827992607",
                "message": "This is a valid message"
            },
            (True, [])
        ),
        (
            {
                "to": "+447827992607",
                "message": "This is a valid message",
                "jobId": 123
            },
            (True, [])
        ),
        (
            {
                "to": "+447827992607",
                "message": "This is a valid message",
                "jobId": 'invalid'
            },
            (False, [{'key': 'jobId', 'message': "'invalid' is not of type 'integer'"}])
        ),
        (
            {
                "to": "+447827992607",
                "message": "a" * 161  # too long
            },
            (False, [{'key': 'message',
                      'message': "'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' is too long"}])  # noqa
        ),
        (
            {
                "to": "+447827992607",
                "message": ""  # too short
            },
            (False, [{'message': "'' is too short", 'key': 'message'}])
        ),
        (
            {
                "to": "+447827992607"  # no message
            },
            (False, [{'required': ["'message' is a required property"]}])
        ),
        (
            {
                "message": "This is a valid message"  # no to field
            },
            (False, [{'required': ["'to' is a required property"]}])
        ),
        (
            {
                # no fields
            },
            (False, [{'required': ["'to' is a required property", "'message' is a required property"]}])
        ),
        (
            {
                "to": "447827992607",  # missing +
                "message": "This is a valid message"
            },
            (False, [{'message': "'447827992607' does not match '^\\\\+44[\\\\d]{10}$'", 'key': 'to'}])
        ),
        (
            {
                "to": "+347827992607",  # not uk
                "message": "This is a valid message"
            },
            (False, [{'key': 'to', 'message': "'+347827992607' does not match '^\\\\+44[\\\\d]{10}$'"}])
        ),
        (
            {
                "to": "07827992607",  # no prefix
                "message": "This is a valid message"
            },
            (False, [{'message': "'07827992607' does not match '^\\\\+44[\\\\d]{10}$'", 'key': 'to'}])
        )
    ]
    yield cases


def test_should_validate_uk_phone_numbers_only(sms_test_cases):
    for case, result in sms_test_cases:
        assert valid_sms_notification(case) == result


@pytest.yield_fixture
def job_test_cases():
    cases = [
        (
            {
                "serviceId": 1234,
                "name": "This is a valid message"
            },
            (True, [])
        ),
        (
            {
                "serviceId": "not-valid",
                "name": "This is a valid message"
            },
            (False, [
                {
                    'key': 'serviceId',
                    'message': "'not-valid' is not of type 'integer'"
                }
            ])
        ),
        (
            {
                "serviceId": 1234,
                "name": "a" * 161  # too long
            },
            (False, [{'key': 'name',
                      'message': "'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' is too long"}])  # noqa
        ),
        (
            {
                "serviceId": 1234,
                "name": "a"
            },
            (False, [{'key': 'name',
                      'message': "'a' is too short"}])
        ),
        (
            {
                "serviceId": 1234,
            },
            (False, [{'required': ["'name' is a required property"]}])
        ),
        (
            {
                "name": "This is a valid message"
            },
            (False, [{'required': ["'serviceId' is a required property"]}])
        ),
    ]
    yield cases


def test_should_validate_job_creation(job_test_cases):
    for case, result in job_test_cases:
        assert valid_job_submission(case) == result


@pytest.yield_fixture
def service_test_cases():
    cases = [
        (
            {
                "organisationId": 1234,
                "name": "This is a valid message"
            },
            (True, [])
        ),
        (
            {
                "organisationId": "not-valid",
                "name": "This is a valid message"
            },
            (False, [
                {
                    'key': 'organisationId',
                    'message': "'not-valid' is not of type 'integer'"
                }
            ])
        ),
        (
            {
                "organisationId": 1234,
                "name": "a" * 161  # too long
            },
            (False, [{'key': 'name',
                      'message': "'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' is too long"}])  # noqa
        ),
        (
            {
                "organisationId": 1234,
                "name": "a"
            },
            (False, [{'key': 'name',
                      'message': "'a' is too short"}])
        ),
        (
            {
                "organisationId": 1234,
            },
            (False, [{'required': ["'name' is a required property"]}])
        ),
        (
            {
                "name": "This is a valid message"
            },
            (False, [{'required': ["'organisationId' is a required property"]}])
        ),
    ]
    yield cases


def test_should_validate_service_creation(service_test_cases):
    for case, result in service_test_cases:
        assert valid_service_submission(case) == result


@pytest.yield_fixture
def user_authentication_test_cases():
    cases = [
        (
            {
                "emailAddress": "valid@email.com",
                "password": "valid-password"
            },
            (True, [])
        ),
        (
            {
                "emailAddress": "@email.com",
                "password": "valid-password"
            },
            (False, [
                {
                    'key': 'emailAddress',
                    'message': "'@email.com' does not match '^[^@^\\\\s]+@[^@^\\\\.^\\\\s]+(\\\\.[^@^\\\\.^\\\\s]+)+$'"
                }
            ])
        ),
        (
            {
                "emailAddress": "valid@email.com"
            },
            (False, [{'required': ["'password' is a required property"]}])
        ),
        (
            {
                "password": "valid-password"
            },
            (False, [{'required': ["'emailAddress' is a required property"]}])
        )
    ]
    yield cases


def test_should_validate_user_authentication(user_authentication_test_cases):
    for case, result in user_authentication_test_cases:
        assert valid_user_authentication_submission(case) == result
