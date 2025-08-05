from azure.cosmos import CosmosClient, exceptions
import os

url = os.getenv("AZURE_COSMOS_URL") != None and os.getenv("AZURE_COSMOS_URL") or "localhost:8081"
key = os.getenv("AZURE_COSMOS_KEY") != None and os.getenv("AZURE_COSMOS_KEY") or "your_default_key"

client = CosmosClient(url, credential=key)

database_name = client.get_database_client("AZURE_COSMOS_DATABASE")
container = database_name.get_container_client("AZURE_COSMOS_PROFILES")

def get_user_profile(user_id):
    try:
        response = container.read_item(item=user_id, partition_key=user_id)
        return response
    except exceptions.CosmosResourceNotFoundError:
        return None
    
def save_user_profile(user_id, profile_data):
    profile_data['id'] = user_id  # Cosmos DB requires an 'id' field
    profile_data['user_id'] = user_id  # Ensure user_id is also stored
    container.upsert_item(profile_data)

def upsert_user_profile(user_id, profile_data):
    existing_profile = get_user_profile(user_id)
    if existing_profile:
        existing_profile.update(profile_data)
        save_user_profile(user_id, existing_profile)
    else:
        save_user_profile(user_id, profile_data)    