import json
import base64
import re

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
                raise BaseException("You must set init_json or (the rule_id with the db context)")
            self.id = rule_id
            rule = self.get_rule_by_id(db)
            if type(rule) != dict:
                raise BaseException(f"{rule}")
            self.json_data = rule
            self.rule_request: MockRequest = MockRequest(data=self.json_data[self.id]["request"])
            self.rule_response: MockResponse = MockResponse(data=self.json_data[self.id]["response"])
            self.uniqueRequestBody : bool = self.json_data[self.id]["uniqueRequestBody"]
        else:
            self.init_json_data = init_json_data
            self.rule_request: MockRequest = MockRequest(data=init_json_data["request"])
            self.rule_response: MockResponse = MockResponse(data=init_json_data["response"])
            self.uniqueRequestBody: bool = init_json_data["uniqueRequestBody"]
            self.id: str = self.generate_rule_id()

    def generate_rule_id(self) -> str:
        pattern = re.compile(r'\s+')
        if self.uniqueRequestBody:
            id_components = f'{"".join(self.rule_request.methods)}{self.rule_request.endpoint}{self.rule_request.body}'
        else:
            id_components = f'{"".join(self.rule_request.methods)}{self.rule_request.endpoint}'
        data = re.sub(pattern, '', id_components)
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
            return {self.id: json.loads(rule)}
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