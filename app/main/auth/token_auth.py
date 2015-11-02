from flask import request, abort
from app.main import get_token_from_headers
from app.models import Token
from functools import wraps


def token_type_required(*types):
    """Ensure that token is off the correct type

    Return 403 if the token

    Should be applied before the `@login_required` decorator:

        @login_required
        @role_required('admin', 'admin-ccs-category')
        def view():
            ...

    """

    def token_decorator(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            token_from_headers = get_token_from_headers(request.headers)

            if not token_from_headers:
                return abort(400, "No credentials supplied")

            token = Token.query.filter(Token.token == token_from_headers).first()
            if not token:
                return abort(403)

            if token.type not in types:
                return abort(403)

            return func(*args, **kwargs)

        return decorated_view

    return token_decorator
