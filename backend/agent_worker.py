# backend/agent_worker.py
import os
import asyncio
from dotenv import load_dotenv

from livekit.agents import Agent, cli, WorkerOptions

load_dotenv()

STT_MODEL = os.getenv("STT_MODEL")  # keep it, but may not work if inference isn't enabled

class STTAgent(Agent):
    def __init__(self):
        super().__init__(instructions="Transcribe user speech and send transcript to UI.")
        print("✅ STTAgent initialized")

    # Different versions fire different callbacks.
    # We'll listen to room audio track and rely on built-in STT events if available.
    async def on_start(self):
        print("✅ Agent started (on_start)")

    async def on_event(self, event):
        # Debug: print any events
        # Some versions may not have on_event
        pass

def main():
    agent = STTAgent()
    # WorkerOptions expects an Agent instance in your version
    cli.run_app(WorkerOptions(agent=agent))

if __name__ == "__main__":
    main()
