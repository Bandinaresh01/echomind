"""
LangGraph StateGraph Agent for EchoMind.
Orchestrates decision-making, tool execution, and multi-step reasoning
using Groq and LangGraph with loop-guard protection.
"""

import json
import logging
from typing import List, Dict, Any, AsyncGenerator
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode

from config.settings import settings
from llm.groq_client import get_groq_llm
from tools import ALL_TOOLS

logger = logging.getLogger("EchoMind.Agent.Graph")


def create_agent_graph():
    """
    Constructs and compiles the LangGraph StateGraph workflow:
      START -> agent -> (conditional: agent_routing)
                         ├── tools -> agent (loop for synthesis)
                         └── END (direct answer)
    """
    # 1. Initialize Groq model instances: bound with tools & direct synthesis
    llm = get_groq_llm(streaming=True, temperature=0.7)
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    # 2. Define Agent node
    def agent_node(state: MessagesState) -> Dict[str, List[BaseMessage]]:
        messages = list(state["messages"])

        # Ensure SystemMessage is always at the head of the context
        if not messages or not isinstance(messages[0], SystemMessage):
            system_msg = SystemMessage(content=settings.SYSTEM_PROMPT)
            messages = [system_msg] + messages

        # Check how many tool calls have already been executed
        executed_tools = [m for m in messages if isinstance(m, ToolMessage)]

        # If tools have already gathered data (max 2 tool rounds), force final synthesis
        if len(executed_tools) >= 2:
            logger.info(f"[LangGraph Node: Agent] Tools already executed ({len(executed_tools)}), forcing synthesis.")
            synthesis_prompt = SystemMessage(
                content="Please synthesize the gathered tool information above into a comprehensive, clear, and friendly Markdown response. Do not call any more tools."
            )
            response = llm.invoke(messages + [synthesis_prompt])
            return {"messages": [response]}

        logger.info(f"[LangGraph Node: Agent] Invoking Groq LLM with {len(messages)} messages")
        response = llm_with_tools.invoke(messages)

        # Null-safety fix: Ensure tool call arguments are always dictionaries
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tc in response.tool_calls:
                if tc.get("args") is None:
                    tc["args"] = {}
            logger.info(f"[LangGraph Node: Agent] Tool call decision: {[tc.get('name') for tc in response.tool_calls]}")
        else:
            logger.info("[LangGraph Node: Agent] Direct response generated (no tools needed)")

        return {"messages": [response]}

    # 3. Define ToolNode
    tool_node = ToolNode(ALL_TOOLS)

    # 4. Define loop-guard routing
    def agent_routing(state: MessagesState):
        messages = state["messages"]
        last_message = messages[-1]

        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return END

        executed_tools = [m for m in messages if isinstance(m, ToolMessage)]
        if len(executed_tools) >= 2:
            return END

        return "tools"

    # 5. Build StateGraph
    workflow = StateGraph(MessagesState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", agent_routing, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")

    compiled_graph = workflow.compile()
    logger.info("LangGraph agent workflow successfully compiled with loop protection.")
    return compiled_graph


# Cached graph instance
_compiled_graph = None


def get_agent_graph():
    """Returns a singleton instance of the compiled LangGraph workflow."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = create_agent_graph()
    return _compiled_graph


def format_chat_history(history: List[Dict[str, str]]) -> List[BaseMessage]:
    """Converts serialized JSON role-content history dicts into LangChain message objects."""
    messages = []
    if not history:
        return messages

    for item in history:
        role = item.get("role", "").lower()
        content = item.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
        elif role == "system":
            messages.append(SystemMessage(content=content))

    return messages


async def stream_agent_events(
    query: str,
    history: List[Dict[str, str]] = None
) -> AsyncGenerator[str, None]:
    """
    Streams Server-Sent Events (SSE) from the LangGraph agent execution.
    """
    if not settings.has_groq_key():
        yield f"data: {json.dumps({'type': 'error', 'content': 'GROQ_API_KEY is not configured in backend/.env.'})}\n\n"
        return

    try:
        graph = get_agent_graph()
    except Exception as e:
        logger.error(f"Failed to initialize LangGraph: {e}")
        yield f"data: {json.dumps({'type': 'error', 'content': f'Failed to initialize LangGraph: {str(e)}'})}\n\n"
        return

    messages: List[BaseMessage] = []
    if history:
        messages.extend(format_chat_history(history))
    messages.append(HumanMessage(content=query))

    tools_used = set()

    try:
        async for event in graph.astream_events(
            {"messages": messages},
            version="v2"
        ):
            kind = event.get("event")

            # 1. Stream token chunks from the ChatGroq model
            if kind == "on_chat_model_stream":
                chunk = event.get("data", {}).get("chunk")
                if chunk and hasattr(chunk, "content") and chunk.content and isinstance(chunk.content, str):
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk.content})}\n\n"

            # 2. Tool started
            elif kind == "on_tool_start":
                tool_name = event.get("name")
                tool_input = event.get("data", {}).get("input")
                if tool_name and tool_name not in ["_Exception"]:
                    tools_used.add(tool_name)
                    yield f"data: {json.dumps({'type': 'tool_start', 'name': tool_name, 'input': tool_input})}\n\n"

            # 3. Tool completed
            elif kind == "on_tool_end":
                tool_name = event.get("name")
                output = str(event.get("data", {}).get("output", ""))
                preview = output[:300] + "..." if len(output) > 300 else output
                if tool_name and tool_name not in ["_Exception"]:
                    yield f"data: {json.dumps({'type': 'tool_end', 'name': tool_name, 'output_preview': preview})}\n\n"

        yield f"data: {json.dumps({'type': 'done', 'tools_used': list(tools_used)})}\n\n"

    except Exception as e:
        logger.error(f"Error during agent execution: {e}", exc_info=True)
        yield f"data: {json.dumps({'type': 'error', 'content': f'Agent execution error: {str(e)}'})}\n\n"


def run_agent(query: str, history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Synchronously invokes the LangGraph agent.
    Returns {"response": str, "tools_used": list[str]}.
    """
    if not settings.has_groq_key():
        return {"response": "GROQ_API_KEY is not configured.", "tools_used": []}

    graph = get_agent_graph()
    messages: List[BaseMessage] = []
    if history:
        messages.extend(format_chat_history(history))
    messages.append(HumanMessage(content=query))

    final_state = graph.invoke({"messages": messages})
    last_msg = final_state["messages"][-1]

    tools_used = []
    for msg in final_state["messages"]:
        if isinstance(msg, ToolMessage):
            tools_used.append(getattr(msg, "name", "tool"))

    return {
        "response": last_msg.content if hasattr(last_msg, "content") else str(last_msg),
        "tools_used": list(dict.fromkeys(tools_used))
    }
