from flask import Blueprint, current_app, request

from mocktails.db import get_db
from mocktails.rules import rules_by_endpoint


mocks = Blueprint('mocks', 'mocks', url_prefix='/')

@mocks.route("/<path:endpoint>", methods=["GET", "DELETE", "PATCH", "POST"])
def mock_request(endpoint):
    endpoint=f"/{endpoint}"
    rules = rules_by_endpoint(endpoint)
    if rules == {}:
        return "Not Found", 404
    for rule_id, rule_data in rules.items():
        if request.method in rule_data["request"]["methods"]:
            return rule_data["response"]["body"], rule_data["response"]["status_code"]
    return "Method Not Allowed", 405