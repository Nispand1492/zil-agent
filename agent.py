# agent.py
from langchain.agents import create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from tools import update_profile
from functools import partial
from langchain.agents import Tool

def get_tools_for_user(user_id: str):
    return [
        Tool.from_function(
            name="AddToListField",
            func=partial(update_profile.add_to_list_field, user_id),
            description="Add an item to a list field. Args: field_name, item"
        ),
        Tool.from_function(
            name="RemoveFromListField",
            func=partial(update_profile.remove_from_list_field, user_id),
            description="Remove an item from a list field. Args: field_name, item"
        ),
        Tool.from_function(
            name="SetStringField",
            func=partial(update_profile.set_string_field, user_id),
            description="Set a string field. Args: field_name, value"
        ),
    ]

def run_agent(prompt: str, user_id: str) -> str:
    tools = get_tools_for_user(user_id)

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You're a helpful assistant for updating job search profiles. Use tools to update fields based on user's natural language input."),
        ("user", "{input}")
    ])

    llm = AzureChatOpenAI(
        # Removed openai_api_version as it is not a valid parameter
        azure_deployment="gpt-35-turbo",         # replace with your actual deployment name
        temperature=0
    )

    agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt_template)

    return agent.invoke({"input": prompt}).output
