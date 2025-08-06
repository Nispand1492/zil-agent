from azure.cosmos import CosmosClient, exceptions
import os

url = os.getenv("AZURE_COSMOS_URL") != None and os.getenv("AZURE_COSMOS_URL") or "localhost:8081"
key = os.getenv("AZURE_COSMOS_KEY") != None and os.getenv("AZURE_COSMOS_KEY") or "your_default_key"

client = CosmosClient(url, credential=key)



def get_user_profile(user_id: str) -> dict:
    try:
        # Existing logic
        container = client.get_database_client("AZURE_COSMOS_DATABASE").get_container_client("AZURE_COSMOS_PROFILES")
        response = container.read_item(user_id, partition_key=user_id)
        return response
    except Exception as e:
        print(f"[ERROR] Failed to load user profile for {user_id}: {e}")
        return {}

def upsert_user_profile(user_id: str, profile_data: dict) -> None:
    container = client.get_database_client("AZURE_COSMOS_DATABASE").get_container_client("AZURE_COSMOS_PROFILES")
    existing_profile = get_user_profile(user_id)
    if not existing_profile:
        print(f"[INFO] No existing profile found for {user_id}, creating a new one.")
    profile_data["user_id"] = user_id
    if existing_profile:
        existing_profile.update(profile_data)
    else:
        existing_profile = profile_data
    container.upsert_item(existing_profile)