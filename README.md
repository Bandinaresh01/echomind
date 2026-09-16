# EchoMind — Production Agentic AI Voice + Text Assistant

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Backend-Flask%203.1-black.svg)](https://flask.palletsprojects.com/)
[![LangGraph](https://img.shields.io/badge/Agent-LangGraph-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Groq](https://img.shields.io/badge/LLM-Groq%20High--Speed%20Inference-green.svg)](https://groq.com/)
[![React](https://img.shields.io/badge/Frontend-React%2019%20%2B%20Vite-61DAFB.svg)](https://react.dev/)
[![LiveKit](https://img.shields.io/badge/Voice-LiveKit%20WebRTC-red.svg)](https://livekit.io/)

EchoMind is a production-grade **Agentic AI Voice + Text Assistant** designed for low-latency reasoning and multi-modal interaction. It couples ultra-fast Groq LPU inference with a stateful **LangGraph** orchestration loop, a standardized **Model Context Protocol (MCP)** tool layer, and a dual-engine voice interface (LiveKit WebRTC + Web Speech API fallback).

---

## 1. Overview & Problem Statement

Modern conversational AI assistants often struggle with two fundamental limitations:
1. **Hallucination & Stale Knowledge**: Static LLM weights lack real-time world context (weather, breaking news, up-to-date web facts).
2. **Rigid Tool Calling Pipelines**: Naive agent implementations execute tools on every request or use inflexible `if/elif` heuristics that fail on nuanced queries.

**EchoMind solves this** by implementing an autonomous decision-making loop powered by LangGraph. The agent dynamically assesses user intent: general questions are answered instantly, while dynamic queries autonomously invoke specialized tools via the **Model Context Protocol (MCP)**, synthesizing multi-tool context into clean, structured Markdown and voice output.

---

## 2. Key Features

- **Agentic Decision Making**: Powered by LangGraph `StateGraph`, deciding when to invoke tools, combine multiple tools, or reply directly.
- **Model Context Protocol (MCP)**: Strict architectural decoupling: `Agent -> Tools -> MCP Client -> MCP Servers -> External APIs`.
- **Comprehensive Tool Ecosystem**:
  - 🌦️ **Weather MCP Server**: OpenWeatherMap API integration with geocoded Open-Meteo fallback.
  - 📰 **News MCP Server**: NewsAPI.org integration with DuckDuckGo news fallback.
  - 🔍 **Search MCP Server**: Live web searching using DuckDuckGo.
  - ⏱️ **Time Tool**: Real-time synchronized system clock.
- **Dual-Engine Voice Interface**:
  - **LiveKit WebRTC**: Token generation and room session handling via `livekit-api`.
  - **Browser Fallback**: Zero-dependency Web Speech API (STT & TTS) so voice functions instantly out of the box.
- **Modern AI SaaS Interface**:
  - Collapsible Sidebar with categorized chat history (*Today*, *Yesterday*, *Previous 7 Days*) stored in `localStorage`.
  - Empty landing screen with clickable prompt chips.
  - Real-time **Tool Activity Cards** showing execution states (`Thinking...`, `Using Weather Tool`, `✓ Completed`).
  - Animated 3D/Canvas **Voice Orb** with dynamic waveform reacting to state machine: `IDLE` -> `CONNECTING` -> `LISTENING` -> `PROCESSING` -> `SPEAKING`.
  - Markdown formatting with code syntax highlighting, copy controls, and voice synthesis.
- **Production Loop-Guard**: Intelligent circuit breaker preventing infinite tool loops and 429 rate limits.

---

## 3. System Architecture

```text
                               ECHOMIND
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
              Text Interaction           Voice Interaction
                    │                           │
                    │                    LiveKit WebRTC
                    │                 (with Web Speech Fallback)
                    │                           │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                         Flask REST Backend
                    (Streaming SSE + Voice Tokens)
                                  │
                                  ▼
                        LangGraph StateGraph
                    (Agent Node + Tool Decision)
                                  │
                                  ▼
                         Groq LLM Client
                   (Ultra-Low-Latency Inference)
                                  │
                           Tool Call Decision
                                  │
                 ┌────────────────┼────────────────┐
                 │                │                │
                 ▼                ▼                ▼
            Weather Tool     Search Tool       News Tool
                 │                │                │
                 └────────────────┼────────────────┘
                                  │
                                  ▼
                       Model Context Protocol (MCP)
                                  │
                 ┌────────────────┼────────────────┐
                 │                │                │
                 ▼                ▼                ▼
            Weather MCP       Search MCP        News MCP
              Server            Server           Server
                 │                │                │
                 ▼                ▼                ▼
          OpenWeatherMap     DuckDuckGo         NewsAPI
            / Open-Meteo       Search         / DDG News
```

---

## 4. LangGraph Agent Workflow

The LangGraph agent compiles a state machine with loop protection:

```text
[START] 
   │
   ▼
[agent] ◄──────────────┐
   │                   │ (tool result context)
   ├───(tool_calls?)───┤
   │                   │
   ▼                   │
 [tools] ──────────────┘
   │
   └──(no tools / max iterations reached)──► [END]
```

### Execution Scenarios:
1. **Direct Answer**: User asks *"What is RAG?"* -> LLM generates explanation without tool calls -> Output rendered.
2. **Single Tool**: User asks *"What is the weather in Hyderabad?"* -> Agent triggers `weather_tool` -> MCP retrieves live temperature (`33.5°C`) -> Agent synthesizes response.
3. **Multi-Tool Synthesis**: User asks *"What is the weather in Hyderabad and what are today's AI news headlines?"* -> Agent calls `weather_tool` + `news_tool` -> MCP gathers data -> Agent synthesizes unified report.

---

## 5. Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS, Framer Motion, Lucide Icons |
| **Backend** | Python 3.12+, Flask 3.1, Flask-CORS, Gunicorn/Werkzeug |
| **Agentic AI** | LangGraph 1.2+, LangChain Core, LangChain Groq |
| **LLM Provider** | Groq (`openai/gpt-oss-120b`, `llama-3.3-70b-versatile`) |
| **MCP Layer** | Model Context Protocol Python Client & Servers |
| **Voice / Real-time** | LiveKit API (WebRTC JWT tokens), Web Speech API (STT & TTS) |
| **External APIs** | OpenWeatherMap, Open-Meteo, NewsAPI.org, DuckDuckGo |
| **Testing & CI** | Pytest, Requests, TestClient |
| **Containers** | Docker, Docker Compose |

---

## 6. Project Structure

```text
EchoMind/
├── backend/
│   ├── app.py                     # Flask application factory, CORS, SPA static serving
│   ├── run.py                     # Backend startup runner (http://localhost:5000)
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py            # Centralized settings, model config, and key validator
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat.py                # POST /api/chat (SSE stream & synchronous mode)
│   │   ├── voice.py               # POST /api/voice/token, GET /api/voice/status
│   │   └── health.py              # GET /health, GET /api/health
│   ├── llm/
│   │   ├── __init__.py
│   │   └── groq_client.py         # Groq ChatGroq client factory & connection reuse
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── client.py              # Unified MCP Client & tool dispatcher
│   │   └── servers/
│   │       ├── __init__.py
│   │       ├── weather_server.py  # Weather MCP server (OpenWeatherMap + fallback)
│   │       ├── search_server.py   # Search MCP server (DuckDuckGo engine)
│   │       └── news_server.py     # News MCP server (NewsAPI + fallback)
│   ├── tools/
│   │   ├── __init__.py            # Exported LangGraph tools (ALL_TOOLS)
│   │   ├── weather.py             # Weather tool bound to MCP
│   │   ├── search.py              # Search tool bound to MCP
│   │   ├── news.py                # News tool bound to MCP
│   │   └── time_tool.py           # System clock tool
│   ├── agents/
│   │   ├── __init__.py
│   │   └── graph.py               # LangGraph StateGraph, ToolNode, loop-guard router
│   ├── tests/
│   │   ├── test_tools.py          # Unit tests for MCP tools
│   │   ├── test_agent.py          # LangGraph decision tests
│   │   └── test_api.py            # Flask integration tests
│   ├── requirements.txt           # Clean production dependencies
│   └── .env.example               # Safe template with placeholders
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx                # Primary routing
│   │   ├── pages/
│   │   │   └── ChatPage.tsx       # Redesigned AI Chat workspace
│   │   ├── components/
│   │   │   ├── Sidebar.tsx        # Collapsible sidebar with chat history
│   │   │   ├── VoiceModal.tsx     # Voice UI with animated orb & waveform
│   │   │   ├── ToolActivityBadge.tsx # Real-time tool execution cards
│   │   │   └── LandingPage.tsx    # Technical architecture landing page
│   │   └── lib/
│   │       ├── useSpeechRecognition.ts
│   │       └── useSpeechSynthesis.ts
│   ├── package.json
│   └── vite.config.ts             # Vite configuration with backend proxy
│
├── .env.example                   # Root environment template
├── .gitignore                     # Protection for .env, caches, node_modules
├── Dockerfile                     # Multi-stage production container
├── docker-compose.yml             # Full stack orchestration (App + LiveKit)
└── README.md
```

---

## 7. Installation & Setup

### Prerequisites
- Python 3.11 or 3.12
- Node.js 18+ and npm

### 1. Clone & Configure Environment
```bash
cp .env.example .env
```
Edit `.env` with your API keys:
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b

WEATHER_API_KEY=your_weather_api_key_here
NEWS_API_KEY=your_news_api_key_here

LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret

SYSTEM_PROMPT="You are EchoMind, an intelligent AI assistant.\n\nRules:\n1. Understand user question.\n2. Decide if you need a tool.\n3. Use search tool for latest information.\n4. Use weather tool for weather questions.\n5. Combine tool results with reasoning.\n6. Give clear answers."
```

### 2. Install Dependencies
**Backend**:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r backend/requirements.txt
```

**Frontend**:
```bash
cd frontend
npm install
npm run build
cd ..
```

---

## 8. Running Locally

### Option A: Unified Production Mode (Recommended)
Run the Flask server which serves both the API and the compiled React UI:
```bash
python backend/run.py
```
Open **`http://localhost:5000`** in your browser.

### Option B: Development Mode (Vite Hot-Reload)
Run Flask in one terminal:
```bash
python backend/run.py
```
Run Vite in a second terminal:
```bash
cd frontend
npm run dev
```
Open **`http://localhost:5173`** (Vite proxies all `/api/*` and `/health` requests to `http://localhost:5000`).

### Option C: Docker Compose
```bash
docker compose up --build
```

---

## 9. Running Automated Tests

Run the test suite inside `backend/`:
```bash
cd backend
python -m pytest tests/ -v
```

---

## 10. Example Queries & Live Verification

| Scenario | User Query | Expected Behavior |
|---|---|---|
| **Direct LLM** | *"Explain artificial intelligence in one sentence."* | Answers immediately with zero tool calls. |
| **Weather Tool** | *"What's the weather in Hyderabad?"* | Triggers `weather_tool` via Weather MCP Server, returns live temp. |
| **News Tool** | *"What are today's latest AI news headlines?"* | Triggers `news_tool` via News MCP Server, formats articles. |
| **Web Search** | *"Search the web for LangGraph updates."* | Triggers `search_tool` via Search MCP Server (DuckDuckGo). |
| **Multi-Tool** | *"What is the weather in Hyderabad and what are today's AI news headlines?"* | Concurrently executes both tools and combines findings into a synthesized response. |
| **Voice Session** | Click *"Talk Live"* or *"Start Voice Session"* | Displays animated orb & waveform; records speech, calls backend, and speaks the answer. |

---

## 11. Interview FAQ / Technical Deep-Dive

- **Why Groq?** Groq’s LPU (Language Processing Unit) architecture delivers generation speeds exceeding 300 tokens/sec, critical for real-time voice streaming where conversational latency must remain sub-second.
- **Why LangGraph over linear chains?** LangGraph provides a cyclical state machine (`StateGraph`), enabling multi-turn tool loops, self-correction, dynamic routing (`tools_condition`), and fine-grained state persistence that linear pipelines cannot achieve.
- **Why Model Context Protocol (MCP)?** Rather than hard-coding external API clients inside agent tool decorators, MCP enforces a clean client-server architecture. Tool implementations can be hosted, versioned, or scaled independently as dedicated services.
- **How does EchoMind prevent infinite tool loops?** EchoMind’s routing function inspects executed `ToolMessage` history, enforcing an automated transition to synthesis if tool recursion depth reaches the safety threshold.
