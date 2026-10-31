import os
import json

def load_config(path: str):
    """Loads a JSON configuration file."""
    with open(path, 'r') as f:
        return json.load(f)

def save_data(data: dict, path: str):
    """Saves data to a JSON file."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

# This file doesn't import agent frameworks, so it shouldn't be flagged.
class Helper:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello from helper {self.name}"
