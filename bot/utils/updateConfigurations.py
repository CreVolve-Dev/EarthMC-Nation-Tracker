import json
import os

import constants

def ensure_dir(path):
    print(f"Checking directory: {path}")
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")

def get_server_config_path(guild_id):
    print(f"Created route to config: {guild_id}.json")
    return os.path.join(constants.SERVER_CONFIGURATION_PATH, f"{guild_id}.json")

def load_server_config(guild_id):
    path = get_server_config_path(guild_id)
    if not os.path.exists(path):
        print(f"Searched for directory: {path}, but was not found")
        return None
    with open(path, "r") as f:
        print(f"Loaded {path}")
        return json.load(f)

def save_server_config(guild_id, data):
    path = get_server_config_path(guild_id)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
        print(f"Saved configurations: {data}, to file: {path}")

def update_configuration(context,
    notifications_channel=None,
    notifications_status=None,
    embed_message=None,
    embed_channel=None,
    citizen_role=None,
    foreign_role=None,
    verified_checkup=None,
    give_verified_role=None,
    tracked_nations=None,
    verified_citizen=None):

    ensure_dir(constants.SERVER_CONFIGURATION_PATH)
    guild_id = str(context.guild.id)

    # List all configurable fields
    fields = [
        "notifications_channel", "notifications_status", "embed_message",
        "embed_channel", "citizen_role", "foreign_role", "verified_checkup",
        "give_verified_role"
    ]
    # Gather arguments into a dict
    params = {k: v for k, v in locals().items() if k in fields and v is not None}
    print(f"Creating parameters object: {params}")

    config = load_server_config(guild_id)
    if config is None:
        # New server config
        config = {"guildName": context.guild.name}
        for k, v in params.items():
            if v is not None:
                config[k] = v
        if tracked_nations is not None:
            config["tracked_nations"] = [tracked_nations]
        else:
            config["tracked_nations"] = []
        if verified_citizen is not None:
            config["verified_citizens"] = [verified_citizen]
        else:
            config["verified_citizens"] = []
        print(f"Creating new configuration object: {config}, for {guild_id}")
    else:
        # Update only provided (not-None) fields
        for k, v in params.items():
            if v is not None:
                config[k] = v
        tracked_nations_list = config.get("tracked_nations")
        if tracked_nations is not None:
            if tracked_nations not in tracked_nations_list:
                tracked_nations_list.append(tracked_nations)
        config["tracked_nations"] = tracked_nations_list

        verified_citizens_list = config.get("verified_citizens")
        if verified_citizen is not None:
            if verified_citizen not in verified_citizens_list:
                verified_citizens_list.append(verified_citizen)
        config["verified_citizens"] = verified_citizens_list
        print(f"Updated configuration object: {config}, for {guild_id}")

    save_server_config(guild_id, config)

def remove_configuration(context,
    notifications_channel=None,
    notifications_status=None,
    embed_message=None,
    embed_channel=None,
    citizen_role=None,
    foreign_role=None,
    verified_checkup=None,
    give_verified_role=None,
    tracked_nations=None,
    verified_citizen=None):

    ensure_dir(constants.SERVER_CONFIGURATION_PATH)
    guild_id = str(context.guild.id)

    fields = [
        "notifications_channel", "notifications_status", "embed_message",
        "embed_channel", "citizen_role", "foreign_role", "verified_checkup",
        "give_verified_role",
    ]

    params = {k: v for k, v in locals().items() if k in fields and v is not None}

    config = load_server_config(guild_id)

    if config is None:
        return None
    else:
        for k, v in params.items():
            config[k] = v
        current_tracked_nations = config.get("tracked_nations")
        if tracked_nations is not None:
            if tracked_nations in current_tracked_nations:
                current_tracked_nations.remove(tracked_nations)
            else:
                return False
        config["tracked_nations"] = current_tracked_nations

        current_verified_citizens = config.get("verified_citizens")
        if verified_citizen is not None:
            if verified_citizen in current_verified_citizens:
                current_verified_citizens.remove(verified_citizen)
            else:
                return False
        config["verified_citizens"] = current_verified_citizens

    save_server_config(guild_id, config)