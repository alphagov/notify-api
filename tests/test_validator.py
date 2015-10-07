from app.main.validators import valid_sms_notificationb
from flask import json
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
            True
        ),
        (
            {
                "to": "+447827992607",
                "message": "a" * 161  # too long
            },
            False
        ),
        (
            {
                "to": "+447827992607",
                "message": ""  # too short
            },
            False
        ),
        (
            {
                "to": "+447827992607"  # no message
            },
            False
        ),
        (
            {
                "message": "This is a valid message"  # no to field
            },
            False
        ),
        (
            {
                "to": "447827992607",  # missing +
                "message": "This is a valid message"
            },
            False
        ),
        (
            {
                "to": "+347827992607",  # not uk
                "message": "This is a valid message"
            },
            False
        ),
        (
            {
                "to": "07827992607",  # no prefix
                "message": "This is a valid message"
            },
            False
        )
    ]
    yield cases


def test_should_validate_uk_phone_numbers_only(sms_test_cases):
    for case, result in sms_test_cases:
        assert valid_sms_notificationb(case) is result
