# THD University Assistant

Voice- and text-enabled admission guidance for Technische Hochschule Deggendorf (THD), built as a Streamlit multi-page app with Gemini, semantic program retrieval, and local session storage.



## What the project does

The assistant helps prospective students explore THD study programs and ask admission-related questions in English or German. It combines a local knowledge base of 93 YAML program files with Gemini-generated answers, optional voice interaction, and a persistent chat history.

Core capabilities:

- Browse and filter 93 THD programs from the Streamlit UI.
- Open a detailed program page with fees, deadlines, contacts, and eligibility data.
- Ask questions in text chat.
- Start a live voice loop that listens, answers, and speaks back.
- Reuse previous answers through a semantic response cache.
- Save, reload, auto-title, and delete chat sessions from `data/sessions/`.

## Current architecture

The app is organized as a Streamlit multi-page frontend plus Python service modules in `src/`.

Main flow:

1. The user opens the app through `Home.py`.
2. `ProgramDataStore` loads the YAML program catalog from `data/programs/`.
3. The assistant page creates `ConversationManager`, `GeminiLLMEngine`, speech-to-text, and text-to-speech components.
4. For each query, the system checks `ResponseCache` first.
5. On a cache miss, `ProgramDataStore` performs semantic retrieval with `sentence-transformers`.
6. Retrieved program data is injected into the Gemini prompt.
7. The response is returned as text and, when enabled, synthesized with Edge TTS.
8. Chat messages are persisted as JSON session files.

## Repository structure

```text
.
|-- Home.py
|-- pages/
|   |-- 1_Program_Search
|   |-- 2_Program_Details
|   |-- 3_Assistant
|   `-- 4_Settings
|-- src/
|   |-- config.py
|   |-- conversation_manager.py
|   |-- data_store.py
|   |-- llm_engine_gemini.py
|   |-- live_chat_worker.py
|   |-- local_voice_handler.py
|   |-- models.py
|   |-- response_cache.py
|   |-- session_manager.py
|   |-- stt_engine_speechrecognition.py
|   |-- tts_engine_edge.py
|   `-- utils/validate_data.py
|-- config/
|   |-- content_index.yaml
|   |-- program_features.yaml
|   `-- query_patterns.yaml
|-- data/
|   |-- programs/
|   |-- cache/
|   `-- sessions/
|-- tests/
|   |-- contract/
|   |-- data/
|   `-- unit/
`-- application-admission-assistant-thd.wiki/
```

## Key modules

- `Home.py`: landing page, language/category state, background styling, and initial data-store loading.
- `pages/1_..._Program_Search.py`: program listing, filtering, pagination, and selection.
- `pages/2_..._Program_Details.py`: detailed program view with category-aware fee display.
- `pages/3_..._Assistant.py`: chat UI, live voice mode, session history sidebar, and assistant wiring.
- `pages/4_..._Settings.py`: language, student category, and basic app status.
- `src/data_store.py`: YAML loading plus semantic search over program metadata.
- `src/llm_engine_gemini.py`: Gemini prompt construction, program-context injection, and Google Search tool usage.
- `src/conversation_manager.py`: cache lookup, LLM request orchestration, context tracking, and TTS cleanup.
- `src/response_cache.py`: exact and semantic response cache backed by `diskcache` when available.
- `src/session_manager.py`: local JSON session CRUD in `data/sessions/`.
- `src/live_chat_worker.py`: background live-chat loop for hands-free voice interaction.

## Technologies in use

- Python 3.9+
- Streamlit
- Google Gemini via `google-genai`
- Sentence Transformers
- scikit-learn
- Pydantic and `pydantic-settings`
- SpeechRecognition
- Edge TTS
- YAML-based content storage
- pytest

## Data model and retrieval

The assistant uses 93 YAML files in `data/programs/` as its primary knowledge base. `ProgramDataStore` parses each file into Pydantic models, indexes them by code and degree level, and builds semantic embeddings with `paraphrase-multilingual-MiniLM-L12-v2`.

Retrieved context is built from fields such as:

- title and degree level
- faculty
- language of instruction
- academic eligibility
- fee information
- intake windows and application dates

## Voice and chat behavior

The project supports two interaction styles:

- Text chat: standard request-response chat inside the assistant page.
- Live chat: a continuous loop managed by `LiveChatWorker` and `LocalVoiceHandler`.

Speech handling currently relies on:

- speech recognition through the `SpeechRecognition` package
- spoken output through `EdgeTTSEngine`
- response cleanup in `ConversationManager._clean_text_for_tts()` so markdown is not spoken literally

## Sessions and cache

Session history is persisted under `data/sessions/` as JSON files. A new session is created automatically when the assistant page is opened from another page. Titles are derived from the first user message.

The response cache is stored under `data/cache/` and supports:

- exact query matches
- semantic query matches using embeddings
- TTL-based expiration
- optional disk persistence via `diskcache`

## Setup

### Prerequisites

- Python 3.9 or newer
- a Gemini API key
- audio input/output support if you want to use voice features

### Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements_streamlit.txt
pip install -r requirements_gemini.txt
pip install -e .
```

Create `.env` in the project root. At minimum:

```env
GEMINI_API_KEY=your_key_here
```

## Run the app

```bash
streamlit run Home.py
```

Default local URL:

```text
http://localhost:8501
```

## Testing

The repository already contains:

- data-quality tests for all YAML program files
- unit tests for core models and session management
- contract-style tests for LLM integration behavior
- a manual voice test checklist

Useful commands:

```bash
pytest
pytest tests/data -v
pytest tests/unit -v
pytest tests/contract -v
```

## Wiki

Project wiki pages live in `application-admission-assistant-thd.wiki/`.

Main pages:

- `home.md`
- `Project_Description.md`
- `Personae.md`
- `Use_Cases.md`
- `Example_Dialogs.md`
- `Flow.md`

## Notes from the current implementation

- The knowledge base size is 93 program files.
- The app is bilingual at the UI and prompt level for English and German.
- Session persistence is local-file based, not database backed.
- The assistant page instantiates `GeminiLLMEngine` with its constructor defaults; if model selection should be fully environment-driven, that wiring still needs to be connected explicitly.


