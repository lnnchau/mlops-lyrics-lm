import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from .core.tools import tts_tool, search_tool
from .core.utils import get_format_response_prompt, get_response_format

llm = ChatOpenAI(base_url=os.environ["OPENAI_BASE_URL"])

agent = create_react_agent(
    llm,
    tools=[tts_tool, search_tool],
    response_format=(get_format_response_prompt(), get_response_format()),
)
