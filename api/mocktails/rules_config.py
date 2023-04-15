import json

from flask import current_app

from mocktails.rules import create_rules, get_all_rules


def import_data(config_file):
    with open(config_file, 'r', encoding='utf-8') as config_data:
        try:
            json_data = "".join(config_data.readlines())
            create_rules(json_data)
        except Exception as e:
            print("Invalid JSON", e)