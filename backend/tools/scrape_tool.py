from langchain.tools import tool
import requests
from bs4 import BeautifulSoup

@tool
def scrape_webpage(url: str) -> str:
    """
    Scrapes the text content of a given webpage URL.
    Provide the exact URL as the argument.
    Use this tool when you need deep specific information from a link found via the search tool!
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=8)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.extract()
            
        text = ' '.join(soup.stripped_strings)
        
        # Limit to roughly 5000 characters to prevent overwhelming the LLM context window
        return text[:5000] if text else "No readable text found on this page."
    except Exception as e:
        return f"Failed to scrape webpage at {url}. Error: {e}"
