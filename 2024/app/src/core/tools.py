from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from openai import OpenAI

openai_client = OpenAI()

search_tool = TavilySearchResults(max_results=2)
