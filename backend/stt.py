#stt.py
import asyncio
import threading
import time
import numpy as np
import whisper

from livekit import rtc
from livekit.api.access_token import AccessToken, VideoGrants


class WhisperRoomSTT:
    """
    Joins a LiveKit room as 'stt-agent', subscribes to audio tracks,
    buffers speech segments, runs local Whisper, and stores last_text.
    """

    def __init__(self, livekit_url: str, api_key: str, api_secret: str, whisper_model: str = "base"):
        self.livekit_url = livekit_url
        self.api_key = api_key
        self.api_secret = api_secret
        self.whisper_model_name = whisper_model

        self.last_text = ""

        self._room_name = None
        self._room: rtc.Room | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._cmd_q: asyncio.Queue = asyncio.Queue()

        self._connected = False
        self._tracks = 0
        self._frames = 0
        self._last_event = ""
        self._last_error = ""

        # Load whisper once
        self._model = whisper.load_model(self.whisper_model_name)

        self._stop_flag = asyncio.Event()

    def start_background(self):
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def _run_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._main())

    async def _main(self):
        while True:
            cmd = await self._cmd_q.get()
            try:
                if cmd["type"] == "connect":
                    await self._connect_room(cmd["room"])
                elif cmd["type"] == "disconnect":
                    await self._disconnect_room()
            except Exception as e:
                self._last_error = f"{type(e).__name__}: {e}"

    def connect(self, room_name: str):
        if not self._loop:
            return
        asyncio.run_coroutine_threadsafe(self._cmd_q.put({"type": "connect", "room": room_name}), self._loop)

    def disconnect(self):
        if not self._loop:
            return
        asyncio.run_coroutine_threadsafe(self._cmd_q.put({"type": "disconnect"}), self._loop)

    def debug_state(self):
        return {
            "room": self._room_name,
            "connected": self._connected,
            "tracks_subscribed": self._tracks,
            "audio_frames": self._frames,
            "last_text": self.last_text,
            "last_event": self._last_event,
            "last_error": self._last_error,
        }

    def _agent_token(self, room_name: str) -> str:
        return (
            AccessToken(self.api_key, self.api_secret)
            .with_identity("stt-agent")
            .with_grants(
                VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=False,
                    can_subscribe=True,
                    can_publish_data=False,
                )
            )
            .to_jwt()
        )

    async def _disconnect_room(self):
        self._last_event = "disconnecting"
        self._stop_flag.set()

        if self._room:
            try:
                await self._room.disconnect()
            except Exception:
                pass

        self._room = None
        self._room_name = None
        self._connected = False
        self._tracks = 0
        self._frames = 0
        self._last_event = "disconnected"
        self._stop_flag = asyncio.Event()

    async def _connect_room(self, room_name: str):
        await self._disconnect_room()

        self._room_name = room_name
        self._last_event = f"connecting:{room_name}"
        self._last_error = ""

        token = self._agent_token(room_name)
        room = rtc.Room()
        self._room = room

        @room.on("connection_state_changed")
        def _on_state_changed(state: rtc.ConnectionState):
            self._last_event = f"state:{state}"
            self._connected = (state == rtc.ConnectionState.CONN_CONNECTED)

        @room.on("track_subscribed")
        def _on_track_subscribed(track: rtc.Track, publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
            if publication.kind == rtc.TrackKind.KIND_AUDIO:
                self._tracks += 1
                self._last_event = f"audio_subscribed:{participant.identity}"
                asyncio.create_task(self._consume_audio(track))

        await room.connect(self.livekit_url, token)
        self._last_event = "connected_waiting_audio"

    async def _consume_audio(self, track: rtc.Track):
        """
        Silence-based segmentation → Whisper transcription.
        """
        # Try to request 16k mono frames (preferred)
        try:
            stream = rtc.AudioStream(track, sample_rate=16000, num_channels=1)
        except TypeError:
            stream = rtc.AudioStream(track)

        # segmentation controls
        RMS_THRESHOLD = 500
        END_SILENCE_MS = 900
        MIN_AUDIO_MS = 700

        in_speech = False
        silence_ms = 0
        audio_ms = 0
        chunks = []

        async for ev in stream:
            if self._stop_flag.is_set():
                break

            frame = ev.frame
            self._frames += 1

            pcm = np.frombuffer(frame.data, dtype=np.int16)

            if getattr(frame, "num_channels", 1) > 1:
                pcm = pcm.reshape(-1, frame.num_channels).mean(axis=1).astype(np.int16)

            rms = int(np.sqrt(np.mean(pcm.astype(np.float32) ** 2)))
            frame_ms = int(1000 * (frame.samples_per_channel / frame.sample_rate))

            if rms > RMS_THRESHOLD:
                in_speech = True
                silence_ms = 0
                chunks.append(pcm)
                audio_ms += frame_ms
            else:
                if in_speech:
                    chunks.append(pcm)
                    silence_ms += frame_ms
                    audio_ms += frame_ms

            if in_speech and silence_ms >= END_SILENCE_MS:
                # finalize utterance
                in_speech = False
                silence_ms = 0

                if audio_ms >= MIN_AUDIO_MS and chunks:
                    await self._transcribe_chunks(chunks, frame.sample_rate)

                chunks = []
                audio_ms = 0

        # flush
        if chunks and audio_ms >= MIN_AUDIO_MS:
            await self._transcribe_chunks(chunks, 16000)

    async def _transcribe_chunks(self, chunks, sample_rate: int):
        try:
            audio_i16 = np.concatenate(chunks)
            audio_f32 = audio_i16.astype(np.float32) / 32768.0

            if sample_rate != 16000:
                # We rely on AudioStream(sample_rate=16000). If not, show diagnostic.
                self._last_error = f"Audio sample_rate={sample_rate} (expected 16000)."
                return

            result = self._model.transcribe(audio_f32, fp16=False, language="en")
            text = (result.get("text") or "").strip()

            if text:
                self.last_text = text
                self._last_event = f"transcribed:{text[:40]}"
        except Exception as e:
            self._last_error = f"{type(e).__name__}: {e}"
        self._loop.run_until_complete(self._main())

    async def _main(self):
        while True:
            cmd = await self._cmd_q.get()
            try:
                if cmd["type"] == "connect":
                    await self._connect_room(cmd["room"])
                elif cmd["type"] == "disconnect":
                    await self._disconnect_room()
            except Exception as e:
                self._last_error = f"{type(e).__name__}: {e}"

    def connect(self, room_name: str):
        if not self._loop:
            return
        asyncio.run_coroutine_threadsafe(self._cmd_q.put({"type": "connect", "room": room_name}), self._loop)

    def disconnect(self):
        if not self._loop:
            return
        asyncio.run_coroutine_threadsafe(self._cmd_q.put({"type": "disconnect"}), self._loop)

    def debug_state(self):
        return {
            "room": self._room_name,
            "connected": self._connected,
            "tracks_subscribed": self._tracks,
            "audio_frames": self._frames,
            "last_text": self.last_text,
            "last_event": self._last_event,
            "last_error": self._last_error,
        }

    def _agent_token(self, room_name: str) -> str:
        return (
            AccessToken(self.api_key, self.api_secret)
            .with_identity("stt-agent")
            .with_grants(
                VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=False,
                    can_subscribe=True,
                    can_publish_data=False,
                )
            )
            .to_jwt()
        )

    async def _disconnect_room(self):
        self._last_event = "disconnecting"
        self._stop_flag.set()

        if self._room:
            try:
                await self._room.disconnect()
            except Exception:
                pass

        self._room = None
        self._room_name = None
        self._connected = False
        self._tracks = 0
        self._frames = 0
        self._last_event = "disconnected"
        self._stop_flag = asyncio.Event()

    async def _connect_room(self, room_name: str):
        await self._disconnect_room()

        self._room_name = room_name
        self._last_event = f"connecting:{room_name}"
        self._last_error = ""

        token = self._agent_token(room_name)
        room = rtc.Room()
        self._room = room

        @room.on("connection_state_changed")
        def _on_state_changed(state: rtc.ConnectionState):
            self._last_event = f"state:{state}"
            self._connected = (state == rtc.ConnectionState.CONN_CONNECTED)

        @room.on("track_subscribed")
        def _on_track_subscribed(track: rtc.Track, publication: rtc.RemoteTrackPublication, participant: rtc.RemoteParticipant):
            if publication.kind == rtc.TrackKind.KIND_AUDIO:
                self._tracks += 1
                self._last_event = f"audio_subscribed:{participant.identity}"
                asyncio.create_task(self._consume_audio(track))

        await room.connect(self.livekit_url, token)
        self._last_event = "connected_waiting_audio"

    async def _consume_audio(self, track: rtc.Track):
        """
        Silence-based segmentation → Whisper transcription.
        """
        # Try to request 16k mono frames (preferred)
        try:
            stream = rtc.AudioStream(track, sample_rate=16000, num_channels=1)
        except TypeError:
            stream = rtc.AudioStream(track)

        # segmentation controls
        RMS_THRESHOLD = 500
        END_SILENCE_MS = 900
        MIN_AUDIO_MS = 700

        in_speech = False
        silence_ms = 0
        audio_ms = 0
        chunks = []

        async for ev in stream:
            if self._stop_flag.is_set():
                break

            frame = ev.frame
            self._frames += 1

            pcm = np.frombuffer(frame.data, dtype=np.int16)

            if getattr(frame, "num_channels", 1) > 1:
                pcm = pcm.reshape(-1, frame.num_channels).mean(axis=1).astype(np.int16)

            rms = int(np.sqrt(np.mean(pcm.astype(np.float32) ** 2)))
            frame_ms = int(1000 * (frame.samples_per_channel / frame.sample_rate))

            if rms > RMS_THRESHOLD:
                in_speech = True
                silence_ms = 0
                chunks.append(pcm)
                audio_ms += frame_ms
            else:
                if in_speech:
                    chunks.append(pcm)
                    silence_ms += frame_ms
                    audio_ms += frame_ms

            if in_speech and silence_ms >= END_SILENCE_MS:
                # finalize utterance
                in_speech = False
                silence_ms = 0

                if audio_ms >= MIN_AUDIO_MS and chunks:
                    await self._transcribe_chunks(chunks, frame.sample_rate)

                chunks = []
                audio_ms = 0

        # flush
        if chunks and audio_ms >= MIN_AUDIO_MS:
            await self._transcribe_chunks(chunks, 16000)

    async def _transcribe_chunks(self, chunks, sample_rate: int):
        try:
            audio_i16 = np.concatenate(chunks)
            audio_f32 = audio_i16.astype(np.float32) / 32768.0

            if sample_rate != 16000:
                # We rely on AudioStream(sample_rate=16000). If not, show diagnostic.
                self._last_error = f"Audio sample_rate={sample_rate} (expected 16000)."
                return

            result = self._model.transcribe(audio_f32, fp16=False, language="en")
            text = (result.get("text") or "").strip()

            if text:
                self.last_text = text
                self._last_event = f"transcribed:{text[:40]}"
        except Exception as e:
            self._last_error = f"{type(e).__name__}: {e}"
