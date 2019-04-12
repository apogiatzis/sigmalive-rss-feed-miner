import os

def config_exists():
    config = os.path.isfile('config.py')
    if not config:
        raise OSError("Config file config.py not found")

def check_config_values(config):
    if not config.PROJECT_ID:
        raise ValueError("PROJECT_ID not set in config")
    elif not config.GITLAB_URL:
        raise ValueError("GITLAB_URL not set in config")
    elif not config.API_KEY:
        raise ValueError("API_KEY not set in config")
    elif not config.EXTRACT_DIR:
        raise ValueError("EXTRACT_DIR not set in config")