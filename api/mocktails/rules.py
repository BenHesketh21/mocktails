from flask import Blueprint, current_app, request, jsonify, send_file

import json

from mocktails.db import get_db


rules = Blueprint('rules', 'rules', url_prefix='/config')

# class Rule():
    
#     def __init__(self, rule_id, json_data):
#         self.json_data = json_data
        
#     def generate_rule_id():
#         self.json_data["request"]["methods"].sort()
        
#         return f'{",".join(self.json_data["request"]["methods"])}:{json_data["request"]["endpoint"]}'
    
#     def split_rule_id():
#         rule_id_split = self.rule_id.split(":")
#         return rule_id_split[0], rule_id_split[1]
    
#     def rule_exists():
#         db = get_db(current_app)
#         existing_rule_ids = db.hkeys("rules")
#         for existing_rule_id in existing_rule_ids:
#             print(existing_rule_id, self.rule_id)
#             existing_methods, existing_endpoint = split_rule_id(existing_rule_id)
#             methods, endpoint = split_rule_id(self.rule_id)
#             if existing_rule_id == self.rule_id or (methods in existing_methods and endpoint == existing_endpoint):
#                 return (True, existing_rule_id)
#         return (False, None)    

def get_all_rules():
    db = get_db(current_app)
    cursor = 0
    rules = {}
    while True:
        print(cursor)
        cursor, rules_scanned = db.hscan("rules", cursor=cursor)
        for id in rules_scanned.keys():
            rules[id] = json.loads(rules_scanned[id])
        if cursor == 0:
            break
    print(rules)
    return rules

def create_rules(json_data):
    db = get_db(current_app)
    rules = json.loads(json_data)
    created_rules = {}
    for rule in rules:
        rule_id = generate_rule_id(rule)
        exists, msg_id = rule_exists(rule_id)
        if exists:
            return {"message": f"Rule {msg_id} already exists"}, 202
        db.hset("rules", rule_id, json.dumps(rule))
        created_rules[rule_id] = rule
    return created_rules
    

def generate_rule_id(rule):
    rule["request"]["methods"].sort()  
    return f'{",".join(rule["request"]["methods"])}:{rule["request"]["endpoint"]}'
    

def rules_by_endpoint(endpoint):
    db = get_db(current_app)
    rules = get_all_rules()
    matched_rules = {}
    for rule_id, rule_data in rules.items():
        if endpoint in rule_data["request"]["endpoint"]:
            matched_rules[rule_id] = rule_data
    return matched_rules

def split_rule_id(rule_id):
    rule_id_split = rule_id.split(":")
    return rule_id_split[0], rule_id_split[1]

def rule_exists(rule_id):
    db = get_db(current_app)
    existing_rule_ids = db.hkeys("rules")
    for existing_rule_id in existing_rule_ids:
        existing_methods, existing_endpoint = split_rule_id(existing_rule_id)
        methods, endpoint = split_rule_id(rule_id)
        if existing_rule_id == rule_id or (methods in existing_methods and endpoint == existing_endpoint):
            current_app.logger.debug(f"Existing: {existing_rule_id}, new: {rule_id}")
            return (True, existing_rule_id)
    return (False, None)

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
    rules = create_rules(request.data)
    return rules

@rules.route("/rule/<path:rule_id>", methods=["DELETE"])
def delete_rule(rule_id):
    db = get_db(current_app)
    rule = db.hget("rules", rule_id)
    db.hdel("rules", rule_id)
    return json.loads(rule)

@rules.route("/rule/<path:rule_id>", methods=["PATCH"])
def update_rule(rule_id):
    db = get_db(current_app)
    rule_data = json.loads(request.data)
    current_app.logger.debug(f"{rule_exists(rule_id)}")
    exists, msg_id = rule_exists(rule_id)
    if not exists:
        return "Rule Not Found", 400
    new_rule_id = generate_rule_id(rule_data)
    exists, msg_id = rule_exists(new_rule_id)
    if exists:
        return {"message": f"Rule {msg_id} already exists"}, 202
    db.hdel("rules", rule_id)
    db.hset("rules", new_rule_id, json.dumps(rule_data))
    return rule_data