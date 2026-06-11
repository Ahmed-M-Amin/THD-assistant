# THD Assistant - Web Application Guide  🎓

Welcome to the interactive web portal for the **Technische Hochschule Deggendorf (THD)** assistant. This guide explains how to launch and navigate the Streamlit-based application.

---

## 🚀 Getting Started

### 1. Installation

Ensure you have Python 3.10+ installed, then run:

```bash
pip install -r requirements_streamlit.txt
```

### 2. Configure Environment

The application requires a **Google Gemini API Key**.
1. Copy `.env.example` to `.env`.
2. Edit `.env` and set your key: `GEMINI_API_KEY=your_key_here`.

### 3. Launch

Start the application from the root directory:

```bash
streamlit run Home.py
```

---

## 📄 Application Layout

The assistant is organized into four main sections:

### 1. 🏠 Home
The landing page provides a high-level overview of the assistant's capabilities and quick navigation links to get started.

### 2. 🔍 Program Search
- **Semantic Search**: Use natural language to find programs (e.g., "AI and management").
- **Smart Filters**: Filter by degree level, language of instruction, or faculty.
- **Comparison**: View multiple program summaries at a glance.

### 3. 📋 Program Details
Once you select a program from the search, this page provides a deep dive into:
- **Eligibility**: Academic and language requirements.
- **Fees**: Cost breakdown for German, EU, and International students.
- **Deadlines**: Application windows for Winter and Summer semesters.
- **Contacts**: Direct links to the admissions and international offices.

### 4. 🤖 AI Assistant (Main Chat)
This is the core interactive component where you can:
- **Text Chat**: Ask any specific question about THD admissions.
- **Live Voice Chat**: Toggle the microphone for a hands-free, continuous conversation experience.
- **History Management**: Use the sidebar to save your current chat or reload a previous session from your history.

---

## ⚙️ Configuration & Preferences

Visit the **Settings** sidebar or page to customize:
- **Language**: Toggle between English and German.
- **Student Category**: Set your category (Domestic/EU/International) once to get personalized fee information throughout the session.
- **Technical Info**: View model versions (Gemini 1.5 Flash) and connection status.

---

## 🔧 Troubleshooting

- **Microphone Issues**: Ensure your browser has permission to access your microphone. If using "Live Chat" locally, ensure your server machine has a working audio input device.
- **API Errors**: Check that your `GEMINI_API_KEY` is active and has sufficient quota.
- **Cache**: If you want to force fresh responses, you can clear the cache in the Settings or by deleting the `/data/cache` folder.

---
**Build with ❤️ for THD Students**
