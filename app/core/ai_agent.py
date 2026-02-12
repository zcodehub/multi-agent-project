from typing import List
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain.agents import create_agent
from langchain_core.messages.ai import AIMessage

from app.config.settings import settings

def get_response_from_ai_agents(llm_id: str, query: List[str], allow_search: bool, system_prompt: str):
    # validate model
    if llm_id not in settings.ALLOWED_MODEL_NAMES:
        raise ValueError(f"Model not allowed: {llm_id}")

    # pick provider from settings mapping
    provider = settings.provider_for(llm_id)

    if provider == "openai":
        # pass API key if available (some LLM wrappers read from env automatically)
        llm = ChatOpenAI(model=llm_id, api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else ChatOpenAI(model=llm_id)
    elif provider == "groq":
        llm = ChatGroq(model=llm_id, api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else ChatGroq(model=llm_id)
    else:
        raise RuntimeError(f"Unsupported provider '{provider}' for model '{llm_id}'")

    # tools (provide credentials if supported)
    tools = []
    if allow_search:
        if hasattr(TavilySearch, "__init__"):
            # pass api key if available - constructor signatures vary by package
            if settings.TAVILY_API_KEY:
                tools.append(TavilySearch(max_results=2, api_key=settings.TAVILY_API_KEY))
            else:
                tools.append(TavilySearch(max_results=2))
        else:
            tools.append(TavilySearch(max_results=2))

    # create agent - do not pass deprecated kwargs
    agent = create_agent(model=llm, tools=tools)

    # supply system prompt via state
    state = {"messages": query, "system_prompt": system_prompt}

    response = agent.invoke(state)

    messages = response.get("messages") if isinstance(response, dict) else None
    if not messages:
        raise Exception(f"Agent returned no messages: {response}")

    ai_messages = [m.content for m in messages if isinstance(m, AIMessage)]
    if not ai_messages:
        raise Exception(f"No AIMessage found in agent response: {response}")

    return ai_messages[-1]