from flask import abort, request


def get_json_from_request(root_element):
    if request.content_type not in [
        'application/json',
        'application/json; charset=UTF-8'
    ]:
        abort(400, "Unexpected Content-Type, expecting 'application/json'")
    data = request.get_json()
    if data is None:
        abort(400, "Invalid JSON; must be a valid JSON object")
    if root_element not in data:
        abort(400, "Invalid JSON; must have {} as root element".format(root_element))
    return data[root_element]
