# backend/user_profiles.py

import json
from pathlib import Path
from datetime import datetime

USERS_DIR = Path("data/users")


def _profile_path(profile_id: str) -> Path:
    return USERS_DIR / f"{profile_id}.json"


def create_profile(profile_name: str) -> dict:
    """
    Create a new local user profile.
    """
    profile_id = profile_name.strip().lower().replace(" ", "_")
    path = _profile_path(profile_id)

    if path.exists():
        raise ValueError("Profile already exists")

    profile_data = {
        "profile_id": profile_id,
        "profile_name": profile_name,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
        "applications": []
    }

    USERS_DIR.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2)

    return profile_data

def load_profile(profile_id: str) -> dict:
    path = _profile_path(profile_id)

    if not path.exists():
        raise FileNotFoundError("Profile not found")

    with open(path, "r", encoding="utf-8") as f:
        profile = json.load(f)

    # 🔥 CRITICAL SAFETY FIX
    if "applications" not in profile:
        profile["applications"] = []

    return profile



def save_profile(profile_data: dict) -> None:
    """
    Persist profile data to disk.
    """
    profile_id = profile_data["profile_id"]
    path = _profile_path(profile_id)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2)


def list_profiles() -> list[str]:
    """
    List all existing profile IDs.
    """
    if not USERS_DIR.exists():
        return []

    return [p.stem for p in USERS_DIR.glob("*.json")]
