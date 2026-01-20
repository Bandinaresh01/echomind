import os
import asyncio
from typing import Callable

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentServer, AgentSession, room_io

load_dotenv()

STT_MODEL = os.getenv("STT_MODEL")
ROOM_NAME = os.getenv("LIVEKIT_ROOM", "echomind-room")

class TranscriberAgent(Agent):
    def __init__(self):
        super().__init__(instructions="Transcribe user speech and emit the transcript only.")

def run_livekit_agent(on_text: Callable[[str], None]):
    print("\n========== EchoMind Agent Boot ==========")
    print("LIVEKIT_URL     =", os.getenv("LIVEKIT_URL"))
    print("LIVEKIT_ROOM    =", ROOM_NAME)
    print("STT_MODEL       =", STT_MODEL)
    print("LIVEKIT_API_KEY =", "SET" if os.getenv("LIVEKIT_API_KEY") else "MISSING")
    print("LIVEKIT_API_SECRET =", "SET" if os.getenv("LIVEKIT_API_SECRET") else "MISSING")
    print("========================================\n")

    server = AgentServer()

    @server.rtc_session()
    async def transcription_job(ctx: agents.JobContext):
        print("✅ Agent job created. Room object:", ctx.room.name)

        session = AgentSession(
            stt=STT_MODEL,
            llm=None,
            tts=None,
        )

        @session.on("user_input_transcribed")
        def _on_transcribed(ev):
            text = getattr(ev, "transcript", None) or getattr(ev, "text", "")
            text = (text or "").strip()
            print("📩 user_input_transcribed event fired. text =", repr(text))
            if text:
                on_text(text)

        # Helpful: log when participants join
        @ctx.room.on("participant_connected")
        def _p_join(p):
            print("👤 Participant connected:", p.identity)

        @ctx.room.on("track_published")
        def _track(pub, participant):
            print("🎧 Track published by:", participant.identity, "| kind:", pub.kind)

        print("✅ Starting session, waiting for mic audio...")
        await session.start(
            room=ctx.room,
            agent=TranscriberAgent(),
            room_options=room_io.RoomOptions(
                audio_input=room_io.AudioInputOptions()
            ),
        )
        print("✅ Session started. Listening...")

        while True:
            await asyncio.sleep(1)

    agents.cli.run_app(server)
