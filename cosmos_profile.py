# cosmos_profile.py

import os
from azure.cosmos import CosmosClient, exceptions

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
# Initialize Cosmos DB client
COSMOS_URL = os.getenv("AZURE_COSMOS_URL")
COSMOS_KEY = os.getenv("AZURE_COSMOS_KEY")


if not COSMOS_URL:
    raise ValueError("Missing environment variable: AZURE_COSMOS_URL")
if not COSMOS_KEY:
    raise ValueError("Missing environment variable: AZURE_COSMOS_KEY")

DATABASE_NAME = "zil_ai"
CONTAINER_NAME = "profiles"



client = CosmosClient(COSMOS_URL, COSMOS_KEY)
db = client.get_database_client(DATABASE_NAME)
container = db.get_container_client(CONTAINER_NAME)

# Load profile for a given user
def get_profile(user_id: str) -> dict:
    try:
        return container.read_item(item=user_id, partition_key=user_id)
    except exceptions.CosmosResourceNotFoundError:
        return create_empty_profile(user_id)

# Save or update profile
def save_profile(user_id: str, profile_dict: dict):
    profile_dict["id"] = user_id
    container.upsert_item(profile_dict)

# Create default empty profile
def create_empty_profile(user_id: str) -> dict:
    profile = {
        "id": user_id,
        "job_titles": [],
        "locations": [],
        "required_skills": [],
        "industries": [],
        "employment_type": [],
        "experience_level": "",
        "certifications": [],
        "must_have_keywords": [],
        "soft_preferences": {
            "company_size": "",
            "work_life_balance": None,
            "diversity_friendly": None
        }
    }
    container.create_item(profile)
    return profile
