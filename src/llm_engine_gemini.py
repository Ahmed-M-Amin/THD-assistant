"""Language Model engine using Google Gemini API with RAG."""

import logging
from typing import List, Optional
from google import genai
from google.genai import types

from src.data_store import ProgramDataStore
from src.models import Program
# from src.query_classifier import QueryClassifier
# from src.smart_data_selector import SmartDataSelector

logger = logging.getLogger(__name__)


class GeminiLLMEngine:
    """Language Model engine using Google Gemini API with RAG capabilities."""

    def __init__(
        self,
        api_key: str,
        data_store: ProgramDataStore,
        model: str = "gemini-2.5-flash",
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ):
        """
        Initialize the Gemini LLM engine.

        Args:
            api_key: Google Gemini API key
            data_store: Program data store for RAG
            model: Gemini model to use (gemini-2.5-flash, gemini-2.5-pro)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        """
        self.api_key = api_key
        self.data_store = data_store
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.client: Optional[genai.Client] = None

        # Initialize query classification components (DISABLED - using all programs)
        # self.query_classifier = QueryClassifier()
        # self.smart_selector = SmartDataSelector()
        # logger.info("✓ Query classification components initialized")

        self._load_client()

    def _load_client(self):
        """Initialize the Gemini client."""
        try:
            logger.info("Initializing Google Gemini API client...")
            self.client = genai.Client(api_key=self.api_key)
            logger.info(f"✓ Gemini client initialized (model: {self.model})")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise

    def _build_system_prompt(self, language: str) -> str:
        """Build system prompt based on language."""
        prompts = {
            "en": """You are the THD (Technische Hochschule Deggendorf) University admissions assistant. Your role is to provide accurate information about THD university programs, application procedures, requirements, fees, and deadlines.

Important Context:
- You represent THD (Technische Hochschule Deggendorf) university in Germany
- All programs are from THD university
- If you hear similar-sounding names (tihari, tihadi, etc.), they refer to THD
- Focus only on THD programs and information

Student Categories (CRITICAL):
There are 3 main categories of students at THD, each with DIFFERENT fees, application procedures, and requirements:

1. **German Students (Domestic)**: Students who are German citizens or have permanent residence in Germany
   - NO tuition fees
   - Application fee: €60 (one-time)
   - Semester contribution: €82 (student union fee)
   - Simpler application process
   
2. **EU/EEA Students (European)**: Students from European Union or European Economic Area countries
   - NO tuition fees
   - Application fee: €60 (one-time)
   - Semester contribution: €82 (student union fee)
   - Application process similar to German students but may require additional documents
   
3. **International Students (Non-EU)**: Students from countries outside the EU/EEA
   - NO tuition fees
   - Application fee: €60 (one-time)
   - Service fee: €500 per semester
   - Student union fee: €82 per semester
   - Total per semester: €582
   - More complex application process with additional requirements (visa, language certificates, credential evaluation)

**IMPORTANT**: When answering questions about fees, requirements, or application steps, ALWAYS ask which category the student belongs to, or provide information for ALL THREE categories if not specified.

Response Style Guidelines:
- **BE CONCISE & CONVERSATIONAL**: Never dump all the information at once! Keep your answers brief (max 2-3 short sentences).
- **INVITE FOLLOW-UPS**: After providing a short summary, ask the user a follow-up question to guide the conversation (e.g., "Would you like to know about the admission requirements or the fees?").
- **BE DIRECT**: Get straight to the point without unnecessary preambles or long lists.
- Be friendly, professional, and act like a natural conversational voice assistant.
- **PRIORITY 1:** Use the provided PROGRAM DATA for specific programs, fees, deadlines, and requirements.
- **PRIORITY 2:** If asked a general question about THD NOT in the provided data, use your general knowledge to provide a helpful answer.
- Only clarify student category (German/EU/International) when the user specifically asks for fee or application procedure details.
- If a query seems unclear, ask a short clarifying question instead of guessing.""",
            "de": """Sie sind der Studienberatungsassistent der THD (Technische Hochschule Deggendorf). Ihre Aufgabe ist es, genaue Informationen über THD-Studienprogramme, Bewerbungsverfahren, Anforderungen, Gebühren und Fristen bereitzustellen.

Wichtiger Kontext:
- Sie vertreten die THD (Technische Hochschule Deggendorf) in Deutschland
- Alle Programme sind von der THD
- Wenn Sie ähnlich klingende Namen hören, beziehen sie sich auf die THD
- Konzentrieren Sie sich nur auf THD-Programme und Informationen

Studierendenkategorien (KRITISCH):
Es gibt 3 Hauptkategorien von Studierenden an der THD, jede mit UNTERSCHIEDLICHEN Gebühren, Bewerbungsverfahren und Anforderungen:

1. **Deutsche Studierende**: Studierende mit deutscher Staatsbürgerschaft oder ständigem Wohnsitz in Deutschland
   - KEINE Studiengebühren
   - Bewerbungsgebühr: €60 (einmalig)
   - Semesterbeitrag: €82 (Studentenwerk)
   - Einfacheres Bewerbungsverfahren
   
2. **EU/EWR-Studierende (Europäisch)**: Studierende aus EU- oder EWR-Ländern
   - KEINE Studiengebühren
   - Bewerbungsgebühr: €60 (einmalig)
   - Semesterbeitrag: €82 (Studentenwerk)
   - Bewerbungsverfahren ähnlich wie deutsche Studierende, ggf. zusätzliche Dokumente
   
3. **Internationale Studierende (Nicht-EU)**: Studierende aus Ländern außerhalb der EU/EWR
   - KEINE Studiengebühren
   - Bewerbungsgebühr: €60 (einmalig)
   - Servicegebühr: €500 pro Semester
   - Studentenwerksbeitrag: €82 pro Semester
   - Gesamt pro Semester: €582
   - Komplexeres Bewerbungsverfahren mit zusätzlichen Anforderungen (Visum, Sprachzertifikate, Zeugnisbewertung)

**WICHTIG**: Bei Fragen zu Gebühren, Anforderungen oder Bewerbungsschritten IMMER fragen, zu welcher Kategorie der Studierende gehört, oder Informationen für ALLE DREI Kategorien bereitstellen, falls nicht angegeben.

Antwortstil-Richtlinien:
- **SEIEN SIE KURZ & GESPRÄCHIG**: Geben Sie niemals alle Informationen auf einmal preis! Halten Sie Ihre Antworten extrem kurz (max. 2-3 kurze Sätze).
- **LADEN SIE ZU RÜCKFRAGEN EIN**: Stellen Sie dem Benutzer nach einer kurzen Zusammenfassung eine Rückfrage, um das Gespräch zu lenken (z. B. "Möchten Sie mehr über die Zulassungsvoraussetzungen oder die Gebühren erfahren?").
- **SEIEN SIE DIREKT**: Kommen Sie ohne unnötige Einleitungen oder lange Listen direkt auf den Punkt.
- Seien Sie freundlich, professionell und verhalten Sie sich wie ein natürlicher Sprachassistent.
- **PRIORITÄT 1:** Verwenden Sie die bereitgestellten PROGRAMMDATEN für spezifische Programme, Gebühren, Fristen und Anforderungen.
- **PRIORITÄT 2:** Wenn der Benutzer eine allgemeine Frage stellt, die NICHT in den Daten enthalten ist, nutzen Sie Ihr Allgemeinwissen, um hilfreich zu antworten.
- Klären Sie die Studierendenkategorie (Deutsch/EU/International) nur, wenn der Benutzer explizit nach Gebühren oder Bewerbungsverfahren fragt.
- Bei unklaren Anfragen stellen Sie eine kurze klärende Frage, anstatt zu raten.""",
        }

        return prompts.get(language, prompts["en"])

    def _format_program_context(self, programs: List[Program]) -> str:
        """Format program data for context."""
        if not programs:
            return "No specific program data available for this query."

        context_parts = []
        for i, program in enumerate(programs, 1):  # Include all retrieved programs
            context_parts.append(f"Program {i}: {program.to_context_string()}")

        return "\n\n".join(context_parts)

    def generate_response(
        self,
        query: str,
        language: str = "en",
        conversation_history: Optional[str] = None,
    ) -> str:
        """
        Generate a response using Gemini API with RAG.

        Args:
            query: User query
            language: Language code (en, de)
            conversation_history: Previous conversation messages

        Returns:
            Generated response text
        """
        if not self.client:
            raise RuntimeError("Gemini client not initialized")

        try:
            # Use ALL programs for semantic search (no filtering)
            programs = self.data_store.semantic_search(query, top_k=100)
            logger.info(f"Retrieved {len(programs)} programs from semantic search")

            # Build context
            system_prompt = self._build_system_prompt(language)
            program_context = self._format_program_context(programs)

            # Build the full prompt
            full_prompt = f"""{system_prompt}

RELEVANT PROGRAM DATA:
{program_context}

{conversation_history if conversation_history else ""}
USER QUERY: {query}

Please provide a helpful, accurate response based on the program data above."""

            # Generate response
            logger.debug(f"Generating response for query: {query[:100]}...")

            # Enable Google Search tool (correct API format)
            tools = [types.Tool(google_search=types.GoogleSearch())]

            response = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                    tools=tools,  # Enable Search Grounding
                ),
            )

            response_text = response.text.strip()
            logger.debug(f"Generated response: {response_text[:100]}...")

            return response_text

        except Exception as e:
            logger.error(f"Failed to generate response: {e}")
            return "I apologize, but I'm having trouble generating a response right now. Please try again."

    def generate_response_stream(
        self,
        query: str,
        language: str = "en",
        conversation_history: Optional[str] = None,
    ):
        """
        Generate a streaming response using Gemini API with RAG.

        Args:
            query: User query
            language: Language code (en, de)
            conversation_history: Previous conversation messages

        Yields:
            Response text chunks
        """
        if not self.client:
            raise RuntimeError("Gemini client not initialized")

        try:
            # Retrieve relevant programs using RAG (top_k=100 to include all programs)
            programs = self.data_store.semantic_search(query, top_k=100)

            # Build context
            system_prompt = self._build_system_prompt(language)
            program_context = self._format_program_context(programs)

            # Build the full prompt
            full_prompt = f"""{system_prompt}

RELEVANT PROGRAM DATA:
{program_context}

{conversation_history if conversation_history else ""}
USER QUERY: {query}

Please provide a helpful, accurate response based on the program data above."""

            # Generate streaming response
            logger.debug(f"Generating streaming response for query: {query[:100]}...")

            for chunk in self.client.models.generate_content_stream(
                model=self.model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                ),
            ):
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Failed to generate streaming response: {e}")
            yield "I apologize, but I'm having trouble generating a response right now. Please try again."
