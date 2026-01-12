import json
import os

USERS_DIR = "users"


def save_user_profile(profile_name: str, profile_data: dict):
    """
    Save user profile data to users/{profile_name}.json
    """
    os.makedirs(USERS_DIR, exist_ok=True)

    file_path = os.path.join(USERS_DIR, f"{profile_name}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=4)
