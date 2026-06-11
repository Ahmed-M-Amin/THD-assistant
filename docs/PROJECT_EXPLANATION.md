# THD University Assistant: Deep Dive Explanation

This document provides a comprehensive technical breakdown of the THD University Assistant, explaining the underlying logic, data flow, and component responsibilities.

## 1. Project Mission
The goal of this project is to provide a **24/7 intelligent admissions officer** for the Technische Hochschule Deggendorf (THD). It bridges the gap between complex PDF/YAML documentation and the user by allowing natural conversation in English or German.

## 2. Core Architecture: RAG-Centric Design
The bot uses **Retrieval-Augmented Generation (RAG)**. Unlike standard chatbots that rely solely on their internal training data, this assistant "looks up" official THD program data before every answer.

### The RAG Pipeline:
1. **Semantic Indexing**: All 93 programs are loaded into the `DataStore`.
2. **Vector Retrieval**: When a query like "Master programs in English" is received, the system converts it into a vector and finds the top matching YAML files.
3. **Prompt Augmentation**: These files are injected into the Gemini 1.5 Flash system prompt as "Ground Truth."
4. **Grounded Generation**: Gemini generates a response restricted to the provided data, effectively eliminating hallucinations.

## 3. Component Deep Dive

### `Home.py` (The Heart)
The main entry point for the Streamlit application. It manages:
- Application initialization and asset loading.
- Global session state (keeping track of language, category, and data store).
- User navigation between the four main pages.

### `src/llm_engine_gemini.py` (The Brain)
Handles the interface with Google's Gemini 1.5 Flash. 
- **System Instructions**: Contains a carefully crafted persona that enforces student categorization (Domestic/EU/International).
- **Search Grounding**: Utilizes the Google Search tool when local YAML data is insufficient for a query.
- **Adaptive Length**: Implements logic to provide concise answers for simple questions and detailed lists for complex ones.

### `src/live_chat_worker.py` (The Continuous Listener)
A specialized asynchronous handler that enables "Live Voice Chat" in Streamlit.
- Runs a background thread that manages the Listen -> Think -> Speak loop.
- Uses `threading.Lock` to safely update the Streamlit session state from the background.
- Detects goodbye phrases to automatically terminate the live session.

### `src/response_cache.py` (The Accelerator)
A performance layer that uses `diskcache`.
- **Similarity Search**: It doesn't just look for exact text matches. It uses semantic similarity (85% threshold) to serve answers for variations of the same question.
- **Latency reduction**: Cuts response time from ~3s to <100ms.

## 4. Interaction Modes

### Standard Text Mode
- **Pattern**: Request -> Response.
- **Best for**: Rapid search and structured reading.

### Live Voice Mode
- **Pattern**: Continuous Loop.
- **Best for**: Hands-free inquiries and natural dialogue.
- **Tech**: Integrated with `Edge-TTS` for natural intonation and `SpeechRecognition` for high-accuracy transcription.

## 5. Directory Roles Recap

| Path | Purpose |
|------|---------|
| `/data/programs` | The "Knowledge Base" (93 YAML files). |
| `/data/sessions` | Persistent storage for user chat history. |
| `/src/models.py` | Pydantic definitions for all data objects (Programs, Messages). |
| `/src/utils` | Scripts for data validation and system maintenance. |
| `/pages` | Streamlit multi-page definitions. |

---
**Maintained by**: THD AI Development Team
**Last Revised**: June 2026
