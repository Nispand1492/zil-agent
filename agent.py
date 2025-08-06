# agent.py
import json
from langchain.agents import create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from tools import update_profile
from functools import partial
from langchain.agents import Tool
from utils.dbutils import get_user_profile



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
        Tool.from_function(
            name="AddPendingQuestion",
            func=partial(update_profile.add_to_list_field, user_id),
            description=(
                "Store a question that the agent should ask the user in the next conversation. "
                "Args: field_name=pending_questions, item"
            )
        ),
        Tool.from_function(
    name="RemovePendingQuestion",
    func=partial(update_profile.remove_from_list_field, user_id),
    description=(
        "Remove a previously stored pending question after it has been answered. "
        "Args: field_name=pending_questions, item"
    )
)
    ]

def run_agent(prompt: str, user_id: str) -> str:
    """
    Runs the agent with the provided prompt and user ID.
    
    Args:
        prompt (str): The natural language input from the user.
        user_id (str): The ID of the user whose profile is being updated.

    Returns:
        str: The output from the agent after processing the prompt.
    """
    
    system_prompt = """
You are an intelligent assistant that helps users build a professional profile by extracting structured data from their conversation.

The profile has the following schema:
- String fields: name, headline, summary, current_title, current_company, location
- List fields: skills, tools, strengths, industries, experience_paragraphs, project_paragraphs, custom_profile_notes

Each time the user shares information, determine if it maps to any field and call the appropriate tool:
- Use SetStringField for string values
- Use AddToListField for adding to list fields
- Do not overwrite list fields directly — always use the add/remove tools
- Be cautious with partial or vague responses. Ask clarifying questions if needed.
- Assume user identity is known (user_id is handled by backend)

If the user answers a question that was previously stored in `pending_questions`, 
call RemovePendingQuestion with that question text to remove it from the list.

"""
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "{prompt}")
    ])

     # Fetch user profile if needed, can be used for context in the agent
    user_profile = get_user_profile(user_id)
    tools = get_tools_for_user(user_id)


    context = {
    "user_profile": json.dumps(user_profile, indent=2),
    "prompt": prompt
}

    llm = AzureChatOpenAI(
        # Removed openai_api_version as it is not a valid parameter
        azure_deployment="gpt-35-turbo",         # replace with your actual deployment name
        temperature=0
    )


    agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt_template)


    # Load profile to fetch pending questions
    pending = user_profile.get("pending_questions", []) if user_profile else []
    # If any pending questions exist, prepend them
    if pending:
        preamble = "Before we continue, I still need to ask:\n" + "\n".join(f"- {q}" for q in pending[:3])
        full_prompt = preamble + "\n\n" + prompt
    else:
        full_prompt = prompt
    try:
        response = agent.invoke({"input": full_prompt})
        return response.content if hasattr(response, "content") else str(response)
    except Exception as e:
        print(f"[ERROR] Agent failed: {e}")
        return "Sorry, something went wrong while processing your request."
