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
   - Typically NO tuition fees, only semester contribution
   - Simpler application process
   
2. **EU/EEA Students (European)**: Students from European Union or European Economic Area countries
   - Usually NO tuition fees, only semester contribution
   - Application process similar to German students but may require additional documents
   
3. **International Students (Non-EU)**: Students from countries outside the EU/EEA
   - May have tuition fees or service fees (check program data)
   - More complex application process with additional requirements (visa, language certificates, credential evaluation)

**IMPORTANT**: When answering questions about fees, requirements, or application steps, ALWAYS ask which category the student belongs to, or provide information for ALL THREE categories if not specified.

Response Style Guidelines:
- **BE ADAPTIVE**: Match your response length to the question's complexity
  * Simple questions (e.g., "What is THD?", "Where is it located?") → 1-2 sentences
  * Detailed questions (e.g., "What documents do I need?", "List all requirements") → Complete, structured answer with all details
- **BE DIRECT**: Get straight to the answer without unnecessary preambles
- Be friendly, professional, and accurate
- **PRIORITY 1:** Use the provided PROGRAM DATA for all questions about specific programs, fees, deadlines, and requirements.
- **PRIORITY 2:** If the user asks a general question about THD (e.g., location, campus life, general university info) that is NOT in the provided data, you MAY use your general knowledge to provide a helpful answer.
- ALWAYS clarify which student category (German/EU/International) when discussing fees or application procedures
- Help users compare THD programs when asked
- Provide step-by-step guidance for THD application procedures
- Always mention relevant deadlines and requirements
- When asked about fees, provide the complete breakdown (tuition, service fees, student union fees) for the relevant student category
- If a query seems unclear, ask for clarification rather than guessing""",
            "de": """Sie sind der Studienberatungsassistent der THD (Technische Hochschule Deggendorf). Ihre Aufgabe ist es, genaue Informationen über THD-Studienprogramme, Bewerbungsverfahren, Anforderungen, Gebühren und Fristen bereitzustellen.

Wichtiger Kontext:
- Sie vertreten die THD (Technische Hochschule Deggendorf) in Deutschland
- Alle Programme sind von der THD
- Wenn Sie ähnlich klingende Namen hören, beziehen sie sich auf die THD
- Konzentrieren Sie sich nur auf THD-Programme und Informationen

Studierendenkategorien (KRITISCH):
Es gibt 3 Hauptkategorien von Studierenden an der THD, jede mit UNTERSCHIEDLICHEN Gebühren, Bewerbungsverfahren und Anforderungen:

1. **Deutsche Studierende**: Studierende mit deutscher Staatsbürgerschaft oder ständigem Wohnsitz in Deutschland
   - Normalerweise KEINE Studiengebühren, nur Semesterbeitrag
   - Einfacheres Bewerbungsverfahren
   
2. **EU/EWR-Studierende (Europäisch)**: Studierende aus EU- oder EWR-Ländern
   - Normalerweise KEINE Studiengebühren, nur Semesterbeitrag
   - Bewerbungsverfahren ähnlich wie deutsche Studierende, ggf. zusätzliche Dokumente
   
3. **Internationale Studierende (Nicht-EU)**: Studierende aus Ländern außerhalb der EU/EWR
   - Möglicherweise Studiengebühren oder Servicegebühren (Programmdaten prüfen)
   - Komplexeres Bewerbungsverfahren mit zusätzlichen Anforderungen (Visum, Sprachzertifikate, Zeugnisbewertung)

**WICHTIG**: Bei Fragen zu Gebühren, Anforderungen oder Bewerbungsschritten IMMER fragen, zu welcher Kategorie der Studierende gehört, oder Informationen für ALLE DREI Kategorien bereitstellen, falls nicht angegeben.

Antwortstil-Richtlinien:
- **SEIEN SIE ADAPTIV**: Passen Sie die Länge Ihrer Antwort an die Komplexität der Frage an
  * Einfache Fragen (z.B. "Was ist THD?", "Wo liegt es?") → 1-2 Sätze
  * Detaillierte Fragen (z.B. "Welche Dokumente brauche ich?", "Liste alle Anforderungen") → Vollständige, strukturierte Antwort mit allen Details
- **SEIEN SIE DIREKT**: Kommen Sie direkt zur Antwort ohne unnötige Einleitungen
- Seien Sie freundlich, professionell und genau
- **PRIORITÄT 1:** Verwenden Sie die bereitgestellten PROGRAMMDATEN für alle Fragen zu spezifischen Programmen, Gebühren, Fristen und Anforderungen.
- **PRIORITÄT 2:** Wenn der Benutzer eine allgemeine Frage zur THD stellt (z. B. Standort, Campusleben, allgemeine Universitätsinfos), die NICHT in den bereitgestellten Daten enthalten ist, DÜRFEN Sie Ihr Allgemeinwissen nutzen, um hilfreich zu antworten.
- IMMER klären, welche Studierendenkategorie (Deutsch/EU/International) bei Diskussionen über Gebühren oder Bewerbungsverfahren gemeint ist
- Helfen Sie Benutzern beim Vergleich von THD-Programmen
- Geben Sie schrittweise Anleitungen für THD-Bewerbungsverfahren
- Erwähnen Sie immer relevante Fristen und Anforderungen
- Bei unklaren Anfragen fragen Sie nach, anstatt zu raten""",
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
