from flask import Blueprint, current_app, request, jsonify, send_file

import json
import base64
import re

from mocktails.db import get_db


rules = Blueprint('rules', 'rules', url_prefix='/config')

class MockRequest():
    def __init__(self, data: dict) -> None:
        self.data: dict = data
        self.methods: list = data["methods"]
        self.methods.sort()
        if "body" in data:
            self.body: dict = data["body"]
        else:
            self.body: str = ""
        self.endpoint: str = data["endpoint"]

class MockResponse():
    def __init__(self, data: dict) -> None:
        self.data: dict = data
        self.status_code: list = data["status_code"]
        self.body: dict = data["body"]

class Rule():
    
    def __init__(self, init_json_data: dict = None, rule_id: str = None, db=None) -> None:
        if init_json_data == None:
            if rule_id == None or db == None:
                raise "You must set init_json or (the rule_id with the db context)"
            self.id = rule_id
            rule = self.get_rule_by_id(db)
            if type(rule) != dict:
                raise f"{rule}"
            self.json_data = rule
            self.rule_request: MockRequest = MockRequest(data=self.json_data["request"])
            self.rule_response: MockResponse = MockResponse(data=self.json_data["response"])
        else:
            self.init_json_data = init_json_data
            self.rule_request: MockRequest = MockRequest(data=init_json_data["request"])
            self.rule_response: MockResponse = MockResponse(data=init_json_data["response"])
            self.id: str = self.generate_rule_id()
        
    def generate_rule_id(self) -> str:
        pattern = re.compile(r'\s+')
        data = re.sub(pattern, '', f'{"".join(self.rule_request.methods)}{self.rule_request.endpoint}{self.rule_request.body}')
        return base64.b64encode(data.encode("utf-8")).decode("utf-8")
    
    def rule_exists(self, db) -> tuple[bool, str]:
        existing_rule_ids = db.hkeys("rules")
        for existing_rule_id in existing_rule_ids:
            if existing_rule_id == self.id:
                return (True, existing_rule_id)
        return (False, None)

    def get_rule_by_id(self, db):
        exists, msg = self.rule_exists(db)
        if exists:
            rule = db.hget("rules", self.id)
            return json.loads(rule)
        return f"Rule {self.id} Doesn't exist"


    def create_rule(self, db) -> tuple[bool, str]:
        exists, msg = self.rule_exists(db)
        if exists:
            return (False, msg)
        db.hset("rules", self.id, json.dumps(self.init_json_data))
        self.json_data = {self.id: self.init_json_data}
        return (True, "")

    def update_rule(self, db, rule: dict) -> tuple[bool, str]:
        current_exists, msg = self.rule_exists(db)
        if current_exists:
            db.hdel("rules", self.id)
            self.rule_request = MockRequest(data=rule["request"])
            self.rule_response = MockResponse(data=rule["response"])
            self.id = self.generate_rule_id()
            db.hset("rules", self.id, json.dumps(rule))
            self.json_data = {self.id: rule}
            return True, f"Updated {self.id}"
        return False, msg

    def delete_rule(self, db) -> bool:
        exists, msg = self.rule_exists(db)
        if exists:
            db.hdel("rules", self.id)
            return True
        return False

def rules_by_endpoint(endpoint: str) -> list[Rule]:
    rules: dict[str, Rule] = get_all_rules()
    matched_rules = []
    for rule_id, rule_data in rules.items():
        rule = Rule(init_json_data=rule_data)
        if endpoint == rule.rule_request.endpoint:
            matched_rules.append(rule)
    return matched_rules


def get_all_rules() -> dict[str, Rule]:
    db = get_db(current_app)
    cursor = 0
    rules: dict[bytes, Rule] = {}
    while True:
        cursor, rules_scanned = db.hscan("rules", cursor=cursor)
        for id in rules_scanned.keys():
            rules[id] = json.loads(rules_scanned[id])
        if cursor == 0:
            break
    return rules

def create_rules(rules: dict) -> dict:
    db = get_db(current_app)
    created_rules = {}
    failed_rules = []
    for rule in rules:
        rule = Rule(init_json_data=rule)
        created_rule, msg = rule.create_rule(db)
        if created_rule:
            created_rules[rule.id] = rule.init_json_data
        else:
            failed_rules.append({"message": f"Rule {msg} already exists"})
    created_rules["errors"] = failed_rules
    return created_rules

@rules.route('/export', methods=["GET"])
def export_rules():
    rules = get_all_rules()
    with open(f'{current_app.config["EXPORT_FOLDER"]}/export.json', 'w+', encoding="utf-8") as export_data:
        export_data.write(json.dumps(rules))
    return send_file(f'{current_app.config["EXPORT_FOLDER"]}/export.json', as_attachment=True)

@rules.route('/rules', methods=["GET"])
def list_rules():
    rules = get_all_rules()
    return rules

@rules.route('/rules', methods=["POST"])
def add_rules():
    rules = create_rules(request.json)
    return rules

@rules.route("/rule", methods=["POST"])
def add_one_rule():
    db = get_db(current_app)
    rule = Rule(init_json_data=json.loads(request.data))
    created_rule, msg = rule.create_rule(db)
    if not created_rule:
        return {"message": f"{msg} already exists"}
    return rule.json_data

@rules.route("/rule/<path:rule_id>", methods=["DELETE"])
def delete_rule(rule_id):
    db = get_db(current_app)
    rule = Rule(rule_id=rule_id, db=db)
    deleted_rule = rule.delete_rule(db)
    if deleted_rule:
        return rule.json_data, 200
    return {"message": f"Rule: {rule_id} doesn't exist"}, 400

@rules.route("/rule/<path:rule_id>", methods=["PATCH"])
def update_rule(rule_id):
    db = get_db(current_app)
    existing_rule = Rule(rule_id=rule_id, db=db)
    new_rule = Rule(init_json_data=json.loads(request.data))
    new_exists, msg = new_rule.rule_exists(db)
    if new_exists:
        return {"message": f"The config for this rule already exists"}, 400
    updated_rule, msg = existing_rule.update_rule(db, new_rule.init_json_data)
    if updated_rule:
        return existing_rule.json_data, 200
    return {"message": f"{rule_id} doesn't exist {e}"}, 400