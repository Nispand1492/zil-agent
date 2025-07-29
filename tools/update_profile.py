import yaml

CONFIG_PATH = "config_zil.yaml"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(config, f)

def update_skill(skill):
    config = load_config()
    if skill not in config["required_skills"]:
        config["required_skills"].append(skill)
        save_config(config)
        return f"Added '{skill}' to skills."
    return f"'{skill}' already in skills."

def update_title(title):
    config = load_config()
    if title not in config["job_titles"]:
        config["job_titles"].append(title)
        save_config(config)
        return f"Added '{title}' to job titles."
    return f"'{title}' already in titles."

def update_location(location):
    config = load_config()
    if location not in config["locations"]:
        config["locations"].append(location)
        save_config(config)
        return f"Added '{location}' to locations."
    return f"'{location}' already in locations."
