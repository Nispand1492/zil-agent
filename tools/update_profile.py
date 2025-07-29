from cosmos_profile import get_profile, save_profile

def add_to_list_field(user_id: str, field_name: str, item: str) -> str:
    profile = get_profile(user_id)
    if item not in profile.get(field_name, []):
        profile.setdefault(field_name, []).append(item)
    save_profile(user_id, profile)
    return f"Added '{item}' to {field_name}."

def remove_from_list_field(user_id: str, field_name: str, item: str) -> str:
    profile = get_profile(user_id)
    if item in profile.get(field_name, []):
        profile[field_name].remove(item)
    save_profile(user_id, profile)
    return f"Removed '{item}' from {field_name}."

def set_string_field(user_id: str, field_name: str, value: str) -> str:
    profile = get_profile(user_id)
    profile[field_name] = value
    save_profile(user_id, profile)
    return f"Set {field_name} to '{value}'."
