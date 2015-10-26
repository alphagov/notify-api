from jsonschema import ValidationError, FormatChecker
from jsonschema.validators import validator_for
from flask import json
import os

JSON_SCHEMAS_PATH = './json_schemas'
SCHEMA_NAMES = [
    'sms',
    'job',
    'service',
    'user_authentication',
    'create_user'
]

FORMAT_CHECKER = FormatChecker()


def load_schemas(schemas_path, schema_names):
    loaded_schemas = {}
    for schema_name in schema_names:
        schema_path = os.path.join(schemas_path, '{}.json'.format(schema_name))

        with open(schema_path) as f:
            schema = json.load(f)
            validator = validator_for(schema)
            validator.check_schema(schema)
            loaded_schemas[schema_name] = schema
    return loaded_schemas


_SCHEMAS = load_schemas(JSON_SCHEMAS_PATH, SCHEMA_NAMES)


def get_validator(schema_name):
    schema = _SCHEMAS[schema_name]
    return validator_for(schema)(schema, format_checker=FORMAT_CHECKER)


def valid_sms_notification(submitted_json):
    return __validate_against_schema('sms', submitted_json)


def valid_job_submission(submitted_json):
    return __validate_against_schema('job', submitted_json)


def valid_service_submission(submitted_json):
    return __validate_against_schema('service', submitted_json)


def valid_user_authentication_submission(submitted_json):
    return __validate_against_schema('user_authentication', submitted_json)


def valid_create_user_submission(submitted_json):
    return __validate_against_schema('create_user', submitted_json)


def __validate_against_schema(schema, submitted_json):
    errors = sorted(get_validator(schema).iter_errors(submitted_json), key=lambda e: e.path)
    if errors:
        return False, __process_errors(errors)
    return True, []


def __process_errors(errors):
    required_field_errors = ([error.message for error in errors if error.schema_path.pop() == 'required'])
    field_errors = [{'key': error.path.pop(), 'message': error.message} for error in errors if error.path]

    for field_error in field_errors:
        if field_error['key'] == 'password':
            field_error['message'] = 'Invalid password'

    if required_field_errors:
        field_errors.append({"required": required_field_errors})

    return field_errors
