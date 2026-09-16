"""
System time tool for LangGraph Agent.
Provides real-time timestamp and date.
"""

import datetime
from langchain_core.tools import tool


@tool
def time_tool() -> str:
    """
    Returns the exact current date, time, and day of the week.
    Use this tool when the user asks for the current time, today's date, or day.
    Takes no arguments.
    """
    now = datetime.datetime.now()
    return f"The current date and time is {now.strftime('%A, %B %d, %Y - %I:%M:%S %p')}."
