import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

from .core.tools import search_tool, wiki_tool
from .core.utils import get_format_response_prompt, get_response_format


llm = ChatOpenAI(base_url=os.environ["OPENAI_BASE_URL"])


agent = create_react_agent(
    llm,
    tools=[search_tool, wiki_tool],
    # response_format=(get_format_response_prompt(), get_response_format()),
)


async def stream_output(query: str):
    messages = [HumanMessage(content=query)]

    async for msg, metadata in agent.astream(
        {"messages": messages},
        stream_mode="messages",
    ):
        if msg.content:
            yield msg.content
