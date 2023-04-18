from flask import Blueprint, current_app, request, send_file

import json

from mocktails.db import get_db
from mocktails.rules.utils import create_rules, get_all_rules
from mocktails.rules.models import Rule


rules = Blueprint('rules', 'rules', url_prefix='/config')

@rules.route('/export', methods=["GET"])
def export_rules():
    db = get_db(current_app)
    rules = get_all_rules(db)
    with open(f'{current_app.config["EXPORT_FOLDER"]}/export.json', 'w+', encoding="utf-8") as export_data:
        export_data.write(json.dumps(rules))
    return send_file(f'{current_app.config["EXPORT_FOLDER"]}/export.json', as_attachment=True)

@rules.route('/rules', methods=["GET"])
def list_rules():
    db = get_db(current_app)
    rules = get_all_rules(db)
    return rules

@rules.route('/rules', methods=["POST"])
def add_rules():
    db = get_db(current_app)
    rules = create_rules(db, request.json)
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
    return {"message": f"{rule_id} doesn't exist"}, 400