from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from openai import OpenAI

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

openai_client = OpenAI()

wiki_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
search_tool = TavilySearchResults(max_results=2)
