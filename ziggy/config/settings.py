import yaml
import os

def load_settings():
    config_path = os.path.join(os.path.dirname(__file__), "settings.yaml")
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

settings = load_settings()
