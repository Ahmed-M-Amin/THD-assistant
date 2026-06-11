# Project Documentation & Structure

## 1. Project Overview
**THD Assistant** is an advanced AI-powered chatbot designed for the Technical University of Deggendorf (THD). It helps students navigate university programs, fees, and requirements using a **RAG (Retrieval-Augmented Generation)** architecture.

The project is built as a modern **Streamlit Web Application**, offering both text and voice interaction modes.

---

## 2. Architecture & Data Flow

The system follows a 5-step pipeline for processing user queries:

1.  **Input**:
    *   **Text**: Typed directly into the chat interface.
    *   **Voice (Standard)**: Captured via a single-trigger microphone transcribed via `SpeechRecognition`.
    *   **Voice (Live Chat)**: Powered by `LiveChatWorker` for a continuous, hands-free loop (Listen → Think → Speak).
2.  **Speech-to-Text (STT)**:
    *   Converts audio to text using **Google Speech Recognition** (via `SpeechRecognition` library).
3.  **RAG & Semantic Search**:
    *   The system searches 93 university program YAML files (`data/programs/`).
    *   Uses **Sentence Transformers** to find the most relevant programs based on the query.
4.  **LLM Processing (Gemini)**:
    *   Constructs a prompt with the retrieved program data (Context).
    *   Sends it to **Google Gemini 1.5 Flash**.
    *   Applies **Google Search Grounding** for up-to-date info outside the local dataset.
    *   Generates a grounded, accurate response.
5.  **Text-to-Speech (TTS)**:
    *   Converts the AI response back to audio using **Edge-TTS** (neural quality).
    *   Plays audio via the browser or local audio device.

---

## 3. Directory Structure

```
thd-assistant/
├── Home.py                       # Streamlit Main Entry Point
├── pages/                        # Streamlit Multi-page App
│   ├── 1_🔍_Program_Search.py    # Search and Filter
│   ├── 2_📋_Program_Details.py   # Detailed View
│   ├── 3_🤖_Assistant.py         # Main Chat Interface
│   └── 4_⚙️_Settings.py          # Preferences
├── src/                          # Core Logic
│   ├── config.py                 # Configuration (Env vars)
│   ├── conversation_manager.py   # Orchestrator (STT -> LLM -> TTS)
│   ├── data_store.py             # RAG Engine (Loads YAMLs)
│   ├── live_chat_worker.py       # Background worker for Live Voice mode
│   ├── local_voice_handler.py    # Microphone & Playback handler
│   ├── llm_engine_gemini.py      # Gemini API Wrapper with RAG & Grounding
│   ├── models.py                 # Pydantic data models
│   ├── response_cache.py         # Semantic response caching
│   ├── session_manager.py        # Chat session persistence (load/save)
│   ├── stt_engine_speechrecognition.py # Speech-to-Text
│   ├── tts_engine_edge.py        # Text-to-Speech
│   └── utils/
│       └── validate_data.py      # Data integrity verification script
├── data/
│   ├── programs/                 # 93 YAML Program Files
│   ├── sessions/                 # Saved chat history (JSON)
│   └── cache/                    # Response Cache
├── config/                       # Application Configs (index, patterns)
├── tests/                        # Comprehensive test suite (850+ tests)
├── assets/                       # UI assets (logo, background)
├── requirements_streamlit.txt    # Web app dependencies
├── requirements_gemini.txt       # AI/Gemini dependencies
└── README.md                     # Main Project README
```

---

## 4. Key Components & Files

### Streamlit Interface
*   **`Home.py`**: Landing page. Initializes session state and global components.
*   **`pages/3_🤖_Assistant.py`**: The core interactive experience.
    *   **Text Mode**: Standard chat.
    *   **Live Chat Mode**: Uses `LiveChatWorker` for continuous voice interaction.
    *   **Session Management**: Sidebar allows loading, saving, and deleting past chats.

### Core Logic (`src/`)
*   **`conversation_manager.py`**: Orchestrates the flow between STT, Gemini, and TTS.
*   **`llm_engine_gemini.py`**: Manages RAG context building and Gemini API calls with Search Grounding enabled.
*   **`live_chat_worker.py`**: Runs an asynchronous background loop on a separate thread to handle real-time voice conversations without freezing the UI.
*   **`data_store.py`**: Performs semantic search across 93 programs using the `paraphrase-multilingual-MiniLM-L12-v2` model.

---

## 5. Technical Features

*   **Semantic Cache**: Uses vector embeddings to match user queries against previous answers, achieving <100ms response times for repeat questions.
*   **Student Category Awareness**: Systematically handles differing requirements/fees for Domestic, EU, and International students.
*   **Adaptive Responses**: LLM is instructed to vary response length based on query complexity.
*   **Persistent Sessions**: Chat histories are stored locally and can be revisited at any time.
