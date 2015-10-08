from app.main.validators import valid_sms_notification
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
                "message": "a" * 161  # too long
            },
            (False, [{'key': 'message', 'message': "'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' is too long"}])  # noqa
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
