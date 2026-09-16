from langchain_community.utilities import ArxivAPIWrapper
from langchain_community.tools.arxiv.tool import ArxivQueryRun

arxiv_tool = ArxivQueryRun(api_wrapper=ArxivAPIWrapper())
