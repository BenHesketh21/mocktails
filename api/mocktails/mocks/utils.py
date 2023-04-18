from mocktails.rules.models import Rule
from mocktails.rules.utils import rules_by_endpoint


def __mock_request(db, endpoint: str, method: str, data: dict) -> tuple[dict, str]:
    endpoint=f"/{endpoint}"
    rules: list[Rule] = rules_by_endpoint(db, endpoint)
    if rules == []:
        return ({"message": "Not Found"}, 404)
    for rule in rules:
        if method in rule.rule_request.methods and (rule.uniqueRequestBody == False or (method == "GET" or data == rule.rule_request.body)):
            return rule.rule_response.body, rule.rule_response.status_code
    return {"message": "Method Not Allowed"}, 405