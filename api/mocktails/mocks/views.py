from flask import Blueprint, current_app, request

from mocktails.db import get_db
from mocktails.mocks.utils import __mock_request



mocks = Blueprint('mocks', 'mocks', url_prefix='/')

@mocks.route("/<path:endpoint>", methods=["GET", "DELETE", "PATCH", "POST"])
def mock_request(endpoint):
    db = get_db(current_app)
    response, status_code = __mock_request(db, endpoint, request.method, request.json)
    return response, status_code