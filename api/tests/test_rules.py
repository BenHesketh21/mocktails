from mocktails import create_app
from mocktails.rules import get_all_rules, create_rules, generate_rule_id, split_rule_id
from mocktails.rules import Rule, MockRequest, MockResponse
from mocktails.db import get_db

from flask import url_for

import pytest
import json

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True
    })
    yield app

def new_rule():
    return Rule(
        init_json_data={
            'request': {
                'body': {}, 
                'endpoint': '/some/endpoint/6',
                 'methods': ['DELETE']
            }, 
            'response': {
                'body': {
                    'boom': 'I AM DELETING'
                }, 
                'status_code': 200
            }
        },

    )

def test_get_empty_rules(app):
    with app.app_context():
        rules = get_all_rules()
        assert rules == {}

def test_add_rule(app):
    with app.app_context():
        new_rule = create_rules(
            json_data='[{"request": {"endpoint": "/some/endpoint/6","methods": ["DELETE"],"body": {} },"response": {"status_code": 200,"body": {"boom": "I AM DELETING"}}}]'
        )
        expected = {'request': {'body': {}, 'endpoint': '/some/endpoint/6', 'methods': ['DELETE']}, 'response': {'body': {'boom': 'I AM DELETING'}, 'status_code': 200}}
        id = generate_rule_id(expected)
        assert new_rule == {id: expected}

def test_generation_of_id(app):
    with app.app_context():
        rule = new_rule()
        id = rule.generate_rule_id()
        assert id == b"eyJib2R5IjogeyJib29tIjogIkkgQU0gREVMRVRJTkcifSwgInN0YXR1c19jb2RlIjogMjAwfQ=="


