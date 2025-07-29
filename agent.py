from langchain.agents import initialize_agent, Tool
from langchain.chat_models import ChatOpenAI
from tools.update_profile import update_skill, update_title, update_location

llm = ChatOpenAI(model="gpt-4", temperature=0)

tools = [
    Tool(name="AddSkill", func=update_skill, description="Add a new required skill"),
    Tool(name="AddTitle", func=update_title, description="Add a new job title to search for"),
    Tool(name="AddLocation", func=update_location, description="Add a new job location to consider"),
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)

def handle_query(query):
    return agent.run(query)
