'''from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from tools import search_tool

load_dotenv()

class ResearchResponse(BaseModel):
    topic:str
    summary: str
    sources:list[str]
    tools_used: list[str]


llm = ChatOpenAI(model="text-davinci-003")
#llm = ChatAnthropic(model="claude-3-sonnet-20240229")
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            you are a researcher assistant that will help generate a research paper.
            answer the user query and use necessary tools.
            Wrap the output in this format and provide no other text\n{format_instructions}
            """,
        ),
        ("placeholder","{chat_history}"),
        ("human","{query} {name}"),
        ("placeholder","{agent_scratchpad}")
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [search_tool]
agent = create_tool_calling_agent(
    llm=llm,
    prompt = prompt,
    tools = [tools]
)
agent_executor = AgentExecutor(agent = agent, tools=tools, verbose=True)
query = input("what can i help you?")
raw_response = agent_executor.invoke({
    "query": query
})

try:
    structured_response = parser.parse(raw_response.get("output")[0]["text"])
    print(structured_response)
except Exception as e:
    print("Error",e)'''

from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent
from langchain.agents import AgentExecutor
from tools import search_tool

load_dotenv()

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

# Corrected model: gpt-3.5-turbo is a valid OpenAI chat model
llm = ChatOpenAI(model="gpt-3.5-turbo")

parser = PydanticOutputParser(pydantic_object=ResearchResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            you are a researcher assistant that will help generate a research paper.
            answer the user query and use necessary tools.
            Wrap the output in this format and provide no other text\n{format_instructions}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}")
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [search_tool]

agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

query = input("what can I help you? ")

raw_response = agent_executor.invoke({
    "query": query
})

try:
    structured_response = parser.parse(raw_response.get("output"))
    print(structured_response)
except Exception as e:
    print("Error:", e)

'''from langchain.agents import initialize_agent, Tool, AgentType
from langchain.llms import OpenAI
import time

# Dummy DB query function - replace this with your actual DB logic or backend API call
def query_database(query: str) -> str:
    # Simulate database processing (replace this with real DB code)
    print(f"Querying database with: {query}")
    time.sleep(1)  # simulate delay
    # Example dummy return
    if "capital of india" in query.lower():
        return "The capital of India is New Delhi."
    elif "team members" in query.lower():
        return "There are currently 150 team members working."
    else:
        return "Sorry, I don't have data on that query."

# Define tools that your agent can call
tools = [
    Tool(
        name="DatabaseQueryTool",
        func=query_database,
        description="Useful for answering questions about the database or backend data."
    ),
]

# Initialize your LLM (make sure OPENAI_API_KEY is set in your env)
llm = OpenAI(temperature=0)

# Initialize the agent with your tools and LLM
agent_executor = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

def main():
    print("Welcome to your Gen AI Project Chatbot!")
    while True:
        user_input = input("What can I help you with? ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        # Run the agent - it can decide whether to call your tools or answer directly
        response = agent_executor.run(user_input)
        print("Agent:", response)

if __name__ == "__main__":
    main()

    
from sqlalchemy.orm import Session
from your_db_models import YourModel

def query_database(query: str) -> str:
    with Session(engine) as session:
        # Parse query and fetch data accordingly
        # This is an example - you’d have real queries or filtering logic
        results = session.query(YourModel).filter(YourModel.name.ilike(f"%{query}%")).all()
        return f"Found {len(results)} results."


import requests

def query_database(query: str) -> str:
    response = requests.get(f"https://your-backend/api/search?q={query}")
    if response.ok:
        data = response.json()
        return f"Backend says: {data.get('answer')}"
    else:
        return "Backend request failed."
'''

