from mocktails import create_app
from mocktails.rules.utils import get_all_rules, create_rules
from mocktails.rules.models import Rule
from mocktails.db import get_db

import pytest
import json

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True
    })
    yield app

def new_rule(db):
    rule = Rule(init_json_data={'uniqueRequestBody': True, 'request': {'body': {}, 'endpoint': '/some/endpoint/6', 'methods': ['DELETE']}, 'response': {'body': {'boom': 'I AM DELETING'}, 'status_code': 200}})
    rule.create_rule(db)
    return rule

def test_get_empty_rules(app):
    with app.app_context() as a:

        db = get_db(a) 
        rules = get_all_rules(db)
        assert rules == {}

def test_add_rule(app):
    with app.app_context() as a:

        db = get_db(a)
        id = 'REVMRVRFL3NvbWUvZW5kcG9pbnQvNnt9'
        expected = {'uniqueRequestBody': True, 'request': {'body': {}, 'endpoint': '/some/endpoint/6', 'methods': ['DELETE']}, 'response': {'body': {'boom': 'I AM DELETING'}, 'status_code': 200}}

        created = create_rules(db, [{'uniqueRequestBody': True, 'request': {'body': {}, 'endpoint': '/some/endpoint/6', 'methods': ['DELETE']}, 'response': {'body': {'boom': 'I AM DELETING'}, 'status_code': 200}}])
        assert created == {id: expected, 'errors': []}

def test_generation_of_id(app):
    with app.app_context() as a:

        db = get_db(a)
        rule = new_rule(db)
        id = rule.generate_rule_id()
        assert id == "REVMRVRFL3NvbWUvZW5kcG9pbnQvNnt9" 

def test_uniqueness_of_rules(app):
    with app.app_context() as a:

        db = get_db(a)
        rule1 = new_rule(db)
        created = rule1.create_rule(db)
        assert created == (False, rule1.id)



