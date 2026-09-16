import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import AgentExecutor
from langchain.agents.output_parsers.tools import ToolsAgentOutputParser
from langchain.agents.format_scratchpad.tools import format_to_tool_messages
from langchain_core.runnables import RunnablePassthrough

from tools.weather import weather_tool
from tools.news import news_tool
from tools.search import search_tool
from tools.time_tool import time_tool
from tools.scrape_tool import scrape_webpage
from tools.finance_tool import finance_tool
from tools.arxiv_tool import arxiv_tool
from tools.gmail_tool import create_read_emails_tool, create_send_email_tool

load_dotenv()

async def get_agent_response_stream(query: str, history: list = None, google_credentials: dict = None, mode: str = "normal"):
    """
    Initializes the agent with the Groq model and available tools,
    and yields Server-Sent Events (SSE) representing tokens and tool usage.
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key or groq_api_key == "your_groq_api_key_here":
        yield f"data: {json.dumps({'type': 'error', 'content': 'GROQ_API_KEY is not set.'})}\n\n"
        return

    llm = ChatGroq(
        groq_api_key=groq_api_key, 
        model_name="openai/gpt-oss-120b",
        streaming=True,
        temperature=1.0
    )

    tools = [weather_tool, news_tool, search_tool, time_tool, scrape_webpage, finance_tool, arxiv_tool]
    
    if google_credentials:
        tools.append(create_read_emails_tool(google_credentials))
        tools.append(create_send_email_tool(google_credentials))

    if mode == "fast":
        SYSTEM_PROMPT = "You are EchoMind, a lightning-fast assistant. Answer the user's query as concisely and directly as possible. Only use tools if strictly necessary. Do not provide long explanations."
        max_iters = 5
    elif mode == "deep":
        SYSTEM_PROMPT = "You are DeepSearch AI, an elite research assistant. You must execute comprehensive multi-step reasoning using multiple tools simultaneously. Synthesize the vastly gathered data into a comprehensive, highly-detailed Markdown report. Do not end your turn prematurely until you have all the facts!"
        max_iters = 30
    else:
        SYSTEM_PROMPT = "You are EchoMind, an elite AI assistant with access to real-time tools: weather, news, search, time clock, webpage scraper, finance tracker, and ArXiv academic paper fetcher. " \
                        "If you have access to `read_recent_emails` and `send_email`, you are explicitly connected to the user's secure Gmail account. Use those tools to check their inbox or send emails on their behalf! " \
                        "CRITICAL: For complex queries you MUST use MULTIPLE tools to gather deep context before answering. Synthesize data into a comprehensive and friendly Markdown response."
        max_iters = 15

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Resolving root cause: Llama-3 drops arguments objects entirely for 0-arg tools, returning None.
    # We intercept generating AIMessages and explicitly convert None arguments to empty dictionaries {}
    # so the ToolsAgentOutputParser doesn't crash throwing AttributeError.
    def fix_null_args(ai_message: AIMessage) -> AIMessage:
        if hasattr(ai_message, "tool_calls"):
            for tc in ai_message.tool_calls:
                if tc.get("args") is None:
                    tc["args"] = {}
        return ai_message

    llm_with_tools = llm.bind_tools(tools)
    
    # Constructing the exact create_tool_calling_agent chain, but embedding our null safety interceptor
    agent = (
        RunnablePassthrough.assign(
            agent_scratchpad=lambda x: format_to_tool_messages(x["intermediate_steps"])
        )
        | prompt
        | llm_with_tools
        | fix_null_args
        | ToolsAgentOutputParser()
    )

    # Set return_intermediate_steps to True to capture the exact tools the agent decided to use
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        return_intermediate_steps=True,
        max_iterations=max_iters,
        handle_parsing_errors=True
    )

    # Convert history dicts into LangChain Message objects
    formatted_history = []
    if history:
        for msg in history:
            if msg.get("role") == "user":
                formatted_history.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "assistant":
                formatted_history.append(AIMessage(content=msg.get("content", "")))

    try:
        async for event in agent_executor.astream_events(
            {"input": query, "chat_history": formatted_history},
            version="v2"
        ):
            kind = event.get("event")
            
            # Stream actual response tokens
            if kind == "on_chat_model_stream":
                chunk_msg = event.get("data", {}).get("chunk")
                if chunk_msg and chunk_msg.content and isinstance(chunk_msg.content, str):
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk_msg.content})}\n\n"
            
            # Identify when a tool is called
            elif kind == "on_tool_start":
                tool_name = event.get("name")
                if tool_name and tool_name not in ["_Exception"]:
                    yield f"data: {json.dumps({'type': 'tool', 'name': tool_name})}\n\n"
                    
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'content': f'An error occurred: {str(e)}'})}\n\n"
