from flask import Blueprint, current_app, request

from mocktails.db import get_db
from mocktails.rules import Rule, rules_by_endpoint



mocks = Blueprint('mocks', 'mocks', url_prefix='/')

@mocks.route("/<path:endpoint>", methods=["GET", "DELETE", "PATCH", "POST"])
def mock_request(endpoint):
    pass
    endpoint=f"/{endpoint}"
    rules: list[Rule] = rules_by_endpoint(endpoint)
    if rules == {}:
        return "Not Found", 404
    for rule in rules:
        if request.method in rule.rule_request.methods and (request.method == "GET" or request.json == rule.rule_request.body):
            return rule.rule_response.body, rule.rule_response.status_code
    return "Method Not Allowed", 405