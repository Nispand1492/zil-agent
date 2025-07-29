import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

from langchain.agents import initialize_agent, Tool, AgentType
from tools.update_profile import update_skill, update_title, update_location
from langchain_openai import AzureChatOpenAI
from pydantic import SecretStr


if os.environ.get("WEBSITE_SITE_NAME"):
    print("Running on Azure App Service")
else:
    print("Running locally")

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=SecretStr(os.getenv("AZURE_OPENAI_API_KEY")), # pyright: ignore[reportArgumentType]
    api_version=os.getenv("AZURE_OPENAI_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT")
)

tools = [
    Tool(name="AddSkill", func=update_skill, description="Add a new required skill"),
    Tool(name="AddTitle", func=update_title, description="Add a new job title to search for"),
    Tool(name="AddLocation", func=update_location, description="Add a new job location to consider"),
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

def handle_query(query):
    return agent.run(query)
