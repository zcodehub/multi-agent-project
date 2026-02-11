from langchain_groq import ChatGroq
# from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_tavily import TavilySearch

from langgraph.prebuilt import create_react_agent
from langchain_core.messages.ai import AIMessage

from app.config.settings import settings

def get_response_from_ai_agents(llm_id , query , allow_search ,system_prompt):

    llm = ChatGroq(model=llm_id)

    tools = [TavilySearch(max_results=2)] if allow_search else []

    # create_react_agent no longer accepts deprecated kwargs like
    # `state_modifier`/`system_prompt` — pass the system prompt in the
    # initial state instead and omit unexpected keyword arguments.
    agent = create_react_agent(
        model=llm,
        tools=tools
    )

    # Provide system prompt inside the agent state so agent implementations
    # that read state can use it. The exact key is implementation-dependent,
    # but most agents accept arbitrary state data; keep it under `system_prompt`.
    state = {"messages": query, "system_prompt": system_prompt}

    response = agent.invoke(state)

    messages = response.get("messages") if isinstance(response, dict) else None

    if not messages:
        raise Exception(f"Agent returned no messages: {response}")

    ai_messages = [message.content for message in messages if isinstance(message, AIMessage)]

    if not ai_messages:
        raise Exception(f"No AIMessage found in agent response: {response}")

    return ai_messages[-1]






