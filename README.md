**Abdrabou, Ahmed, <22304330>** **Project Repository:**  https://mygit.th-deg.de/aa18330/application-admission-assistant-thd


# 🎓 THD University Assistant

> An intelligent, voice-enabled chatbot for Technische Hochschule Deggendorf (THD) university admissions and program information

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.30+-FF4B4B.svg)](https://streamlit.io)
[![Google Gemini](https://img.shields.io/badge/google-gemini--2.5--flash-4285F4.svg)](https://ai.google.dev/)


## Wiki links
- Home: https://mygit.th-deg.de/aa18330/application-admission-assistant-thd/-/wikis/home
- Personae: https://mygit.th-deg.de/aa18330/application-admission-assistant-thd/-/wikis/Personae
- Use cases: https://mygit.th-deg.de/aa18330/application-admission-assistant-thd/-/wikis/Use_Cases
- Example Dialogs : https://mygit.th-deg.de/aa18330/application-admission-assistant-thd/-/wikis/Example_Dialogs
- Dialog Flow : https://mygit.th-deg.de/aa18330/application-admission-assistant-thd/-/wikis/Dialog_Flow


## 📋 Overview

THD University Assistant is a comprehensive, AI-powered chatbot designed to help prospective students navigate the admissions process at Technische Hochschule Deggendorf. Built with Google's Gemini 2.5 Flash LLM and Streamlit, it provides accurate, context-aware answers about university programs, requirements, fees, and deadlines in both English and German.

### ✨ Key Features

- 🎤 **Voice Interaction**: Speak naturally using Speech-to-Text (STT) and hear responses via Text-to-Speech (TTS)
- 🧠 **RAG-Powered Intelligence**: Retrieval-Augmented Generation using 93 YAML program files for accurate, data-grounded responses
- 🌍 **Bilingual Support**: Seamless English and German language support
- 🔍 **Advanced Program Search**: Filter and compare programs by degree level, faculty, language, and more
- 💬 **Session Management**: Persistent chat history with load, save, and delete functionality
- ⚡ **Response Caching**: Intelligent caching for faster repeated queries
- 🎯 **Adaptive Responses**: Smart length adjustment - concise for simple questions, detailed for complex ones
- 🧪 **Comprehensive Testing**: Unit, integration, contract, and end-to-end tests

## 🏗️ Architecture

### Tech Stack

| Component | Technology |
|-----------|------------|
| **Web Framework** | Streamlit 1.30+ |
| **LLM** | Google Gemini 2.5 Flash |
| **RAG** | Sentence Transformers + scikit-learn |
| **STT** | Google Cloud Speech + SpeechRecognition |
| **TTS** | Edge-TTS + gTTS |
| **Data Validation** | Pydantic 2.0+ |
| **Data Format** | YAML (93 program files) |
| **Caching** | diskcache |
| **Testing** | pytest + pytest-mock |

### Project Structure

```
thd-assistant/
├── Home.py                    # Main Streamlit entry point
├── pages/                     # Streamlit multi-page app
│   ├── 1_🔍_Program_Search.py
│   ├── 2_📋_Program_Details.py
│   ├── 3_🤖_Assistant.py
│   └── 4_⚙️_Settings.py
├── src/                       # Core application logic
│   ├── config.py             # Application settings
│   ├── models.py             # Pydantic data models
│   ├── data_store.py         # YAML data management
│   ├── llm_engine_gemini.py  # Gemini LLM integration + RAG
│   ├── conversation_manager.py  # Conversation flow orchestration
│   ├── session_manager.py    # Chat session persistence
│   ├── response_cache.py     # Response caching logic
│   ├── stt_engine_speechrecognition.py  # Speech-to-Text
│   ├── tts_engine_edge.py    # Text-to-Speech
│   └── local_voice_handler.py  # Microphone interaction
├── data/
│   └── programs/             # 93 YAML program files
├── config/                    # Configuration files
│   ├── content_index.yaml    # Program index
│   ├── program_features.yaml # Feature definitions
│   └── query_patterns.yaml   # Query classification patterns
├── assets/                    # UI assets (logo, background)
├── tests/                     # Comprehensive test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   ├── contract/             # LLM contract tests
│   ├── e2e/                  # End-to-end tests
│   └── data/                 # Data quality tests
├── requirements_streamlit.txt  # Web app dependencies
├── requirements_gemini.txt     # Gemini API dependencies
├── pyproject.toml             # Build configuration
├── pytest.ini                 # Test configuration
└── .env.example              # Environment variable template
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **FFmpeg** (for audio processing)
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
- **Google Gemini API Key** ([Get one here](https://ai.google.dev/))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/thd-assistant.git
   cd thd-assistant
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   # For Streamlit web app
   pip install -r requirements_streamlit.txt
   
   # OR for Gemini API integration (includes Streamlit deps)
   pip install -r requirements_gemini.txt
   ```

4. **Install the project in editable mode**
   ```bash
   pip install -e .
   ```

5. **Configure environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your API keys
   ```

   Required `.env` contents:
   ```env
   # Google Gemini API
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # Optional: Google Cloud Speech-to-Text
   GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
   ```

## 💻 Usage

### Web Application (Streamlit)

```bash
streamlit run Home.py
```

The app will open in your browser at `http://localhost:8501`

### Features Overview

#### 1. **Program Search** 🔍
- Filter by degree level (Bachelor, Master, Doctoral)
- Filter by faculty, language, duration, ECTS
- Compare multiple programs side-by-side

#### 2. **Program Details** 📋
- View comprehensive program information
- See admission requirements, fees, deadlines
- Access faculty contact information

#### 3. **AI Assistant** 🤖
Two interaction modes:
- **Text Mode**: Type questions and get instant answers
- **Live Chat Mode**: Voice conversation with STT + TTS

Example questions:
- "What programs are available in Computer Science?"
- "How much are the tuition fees for international students?"
- "What documents do I need to apply as an EU student?"
- "When is the application deadline for Master's programs?"

#### 4. **Settings** ⚙️
- Select language (English/German)
- Choose student category (Domestic/EU/International)
- Configure voice preferences
- Manage session history

## 🧪 Testing

The project includes a comprehensive test suite:

```bash
# Run all tests
python -m pytest

# Run specific test categories
python -m pytest tests/unit/          # Unit tests
python -m pytest tests/integration/   # Integration tests
python -m pytest tests/contract/      # LLM contract tests
python -m pytest tests/data/          # Data quality tests

# Run with verbose output
python -m pytest -v

# Run tests with specific markers
python -m pytest -m "data_quality"
```

**Test Coverage:**
- ✅ 664 tests passing
- ✅ 93 YAML files validated
- ✅ LLM contract tests (no API costs)
- ✅ Unit tests for all core modules
- ✅ Integration tests for conversation flow

## 📊 Data Management

### Program Data

All 93 university programs are stored as YAML files in `data/programs/`. Each file contains:
- Program code, title, degree level
- Faculty, duration, ECTS credits
- Admission requirements
- Fee structure (Domestic/EU/International)
- Language of instruction
- Application deadlines
- Contact information

### Data Validation

Run data quality tests to verify YAML integrity:
```bash
python -m pytest tests/data/test_yaml_validation.py -v
```

## 🔧 Configuration

### Application Settings (`src/config.py`)

```python
PROGRAMS_DATA_PATH = "data/programs"  # YAML program files
CONFIG_PATH = "config/content_index.yaml"  # Program index
MODEL_NAME = "gemini-2.5-flash"  # LLM model
MAX_TOKENS = 2048  # Response length limit
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | ✅ Yes |
| `GOOGLE_APPLICATION_CREDENTIALS` | Google Cloud credentials path | ❌ Optional (for Google STT) |

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add unit tests for new features
- Update documentation as needed
- Run `pytest` before submitting PR



## 🙏 Acknowledgments

- **Technische Hochschule Deggendorf** for program data
- **Google Gemini** for LLM capabilities
- **Streamlit** for the web framework
- **Edge-TTS** for high-quality text-to-speech


---

**Built with ❤️ for students exploring THD programs**
