EchoMind – Voice-Driven AI Assistant with Tool-Aware Reasoning

EchoMind is a voice-enabled, real-time AI assistant built as a B.Tech major project.
It accepts live voice input via LiveKit, converts speech to text using OpenAI Whisper, intelligently routes user queries using Google Gemini LLM, and dynamically invokes external tools (weather, news, web search) to generate accurate, contextual responses.

The project focuses on system-level AI orchestration, tool-aware LLM reasoning, and real-time voice interaction, rather than model fine-tuning.

🚀 Key Features

🎤 Live Voice Input using LiveKit (Docker-based)

🧠 Speech-to-Text with OpenAI Whisper (local, edge execution)

🤖 LLM Reasoning using Google Gemini (tool-aware decision making)

🛠️ Dynamic Tool Invocation

Weather lookup

News summarization

Web search

🔐 Secure Credential Handling (environment variables, JWT)

⚡ Low-latency Responses (real-time interaction)

🧩 Modular & Extensible Architecture

🏗️ System Architecture
Browser (Mic)
   ↓
LiveKit (Docker)
   ↓
Flask Backend
   ↓
Whisper (Speech → Text)
   ↓
LLM Router (Gemini)
   ├── weather_tool
   ├── news_tool
   ├── web_search_tool
   └── llm_only
   ↓
Final Answer → Browser

🧠 Technologies Used
Backend

Python 3.10+

Flask

LiveKit API

OpenAI Whisper (base model)

Google Gemini (gemini-1.5-flash)

Requests, BeautifulSoup

Frontend

HTML / CSS / JavaScript

LiveKit Client SDK

Infrastructure

Docker (LiveKit server)

Environment variables (.env)

JWT-based authentication

📁 Project Structure
echomind_majorproject/
│
├── backend/
│   ├── app.py                # Flask server
│   ├── config.py             # Environment configuration
│   ├── llm.py                # Gemini LLM integration
│   ├── llm_router.py         # Tool decision logic
│   ├── stt.py                # Whisper + LiveKit STT worker
│   └── tools/
│       ├── weather_tool.py
│       ├── news_tool.py
│       └── web_search_tool.py
│
├── templates/
│   └── index.html             # UI
│
├── static/
│   ├── style.css
│   └── main.js
│
├── .env.example
├── .gitignore
└── README.md

⚙️ Setup Instructions
1️⃣ Clone Repository
git clone https://github.com/your-username/echomind.git
cd echomind

2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

🐳 LiveKit Setup (Docker)

Pull and run LiveKit server:

docker pull livekit/livekit-server
docker run -d \
  --name livekit \
  -p 7880:7880 \
  -p 7881:7881 \
  -e LIVEKIT_KEYS="devkey:devsecret" \
  livekit/livekit-server \
  --dev


Verify LiveKit:

http://localhost:7880

🔐 Environment Configuration

Create a .env file:

LIVEKIT_URL=ws://localhost:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=devsecret

GOOGLE_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash

NEWS_API_KEY=your_newsapi_key


❗ Never commit .env to GitHub

▶️ Run the Application
python backend/app.py


Open in browser:

http://localhost:5000

🧪 Evaluation Summary
Task Category	Success Rate	Avg Latency
Weather Retrieval	97%	1.7s
News Summarization	91%	2.1s
Web Search	89%	2.4s
General Knowledge	93%	1.8s
Overall	93.5%	1.9–2.7s

Failures primarily occurred due to external API rate limits and network latency, handled through graceful error messages.

🔒 Security Considerations

API keys stored as environment variables

.env excluded via .gitignore

TLS/HTTPS for external services

LiveKit secured using short-lived JWT tokens

Supports manual key rotation without code changes

🧠 Models Used

Google Gemini: gemini-1.5-flash (inference-only, no fine-tuning)

OpenAI Whisper: base model (local, no fine-tuning)

All task behavior is controlled via prompt engineering and system orchestration.

🚧 Limitations

No offline LLM fallback (depends on Gemini API availability)

External APIs may impose rate limits

Whisper accuracy may degrade in very noisy environments

🔮 Future Enhancements

Context persistence across sessions

Caching for tool responses

Offline / open-source LLM support

Speaker diarization

Mobile-first UI

Advanced fallback & retry strategies

👨‍🎓 Academic Context

Degree: B.Tech (Major Project)

Focus Areas:

Real-time AI systems

Voice interfaces

Tool-augmented LLMs

System integration over model training

📜 License

This project is intended for academic and learning purposes.
