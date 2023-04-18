from flask import current_app

import json

from mocktails.db import get_db
from mocktails.rules.models import Rule


def rules_by_endpoint(db, endpoint: str) -> list[Rule]:
    rules: dict[str, Rule] = get_all_rules(db)
    matched_rules = []
    for rule_id, rule_data in rules.items():
        rule = Rule(init_json_data=rule_data)
        if endpoint == rule.rule_request.endpoint:
            matched_rules.append(rule)
    print(matched_rules)
    return matched_rules


def get_all_rules(db) -> dict[str, Rule]:
    cursor = 0
    rules: dict[bytes, Rule] = {}
    while True:
        cursor, rules_scanned = db.hscan("rules", cursor=cursor)
        for id in rules_scanned.keys():
            rules[id] = json.loads(rules_scanned[id])
        if cursor == 0:
            break
    return rules

def create_rules(db, rules: dict) -> dict:
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

def import_data(config_file):
    with open(config_file, 'r', encoding='utf-8') as config_data:
        try:
            json_data = "".join(config_data.readlines())
            create_rules(json_data)
        except Exception as e:
            print("Invalid JSON", e)