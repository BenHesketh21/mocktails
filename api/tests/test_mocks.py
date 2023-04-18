from mocktails.db import get_db
from mocktails.mocks.utils import __mock_request

from tests.test_rules import new_rule, app


def test_mock_request(app):
    with app.app_context() as a:
        db = get_db(a)
        rule = new_rule(db)
        response, status_code = __mock_request(db, 'some/endpoint/6', 'DELETE', {})
        assert response == {'boom': 'I AM DELETING'}
        assert status_code == 200

def test_mock_with_no_rules(app):
    with app.app_context() as a:
        db = get_db(a)
        response, status_code = __mock_request(db, 'some/endpoint/6', 'DELETE', {})
        assert response == {"message": "Not Found"}
        assert status_code == 404

def test_wrong_method(app):
    with app.app_context() as a:
        db = get_db(a)
        rule = new_rule(db)
        response, status_code = __mock_request(db, 'some/endpoint/6', 'GET', {})
        assert response == {'message': 'Method Not Allowed'}
        assert status_code == 405