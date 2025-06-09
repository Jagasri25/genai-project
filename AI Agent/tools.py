from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import tool
from datetime import datetime


search = DuckDuckGoSearchRun()

@tool
def search_tool(query: str) -> str:
    """Search for the information"""
    return search.run(query)
