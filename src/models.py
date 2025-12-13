"""Pydantic models for program data and conversation context."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime


class ApplicationWindow(BaseModel):
    """Application window with start and end dates."""

    start: str
    end: str


class Intake(BaseModel):
    """Program intake information."""

    term: str  # "winter" or "summer"
    application_window: ApplicationWindow


class ApplicationPortal(BaseModel):
    """Application portal information."""

    label: str
    url: str


class Contacts(BaseModel):
    """Contact information for the program."""

    programme_page: Optional[str] = None
    admissions_email: Optional[str] = None
    international_office_email: Optional[str] = None
    office_hours_url: Optional[str] = None


class LanguageRequirement(BaseModel):
    """Language
    requirement details."""

    minimum_level: str
    accepted_proofs: List[str]


class LanguageRequirements(BaseModel):
    """Language requirements for program admission."""

    notes: Optional[str] = None
    german: Optional[LanguageRequirement] = None
    english: Optional[LanguageRequirement] = None


class AcademicBackground(BaseModel):
    """Academic background requirements."""

    bachelor: Optional[Dict[str, List[str]]] = None
    master: Optional[Dict[str, List[str]]] = None


class ProgrammeSpecificRequirements(BaseModel):
    """Programme-specific requirements."""

    description: Optional[str] = None


class Eligibility(BaseModel):
    """Eligibility requirements for program admission."""

    academic_background: AcademicBackground
    language_requirements: LanguageRequirements
    programme_specific_requirements: Optional[ProgrammeSpecificRequirements] = None


class FeeCategory(BaseModel):
    """Fee information for a specific applicant category."""

    student_union_per_semester: Optional[str] = None
    tuition_per_semester: Optional[str] = None
    other_fees: Optional[List[str]] = Field(default_factory=list)
    application_fee_one_time: Optional[str] = None
    service_fee_per_semester: Optional[str] = None


class Fees(BaseModel):
    """Fee structure for different applicant categories."""

    domestic_german: FeeCategory
    eu_eea: FeeCategory
    international_non_eu: FeeCategory


class RequiredDocuments(BaseModel):
    """Required documents for application."""

    bachelor: Optional[Dict[str, List[str]]] = None
    master: Optional[Dict[str, List[str]]] = None


class Policies(BaseModel):
    """Program policies."""

    late_documents: Optional[str] = None
    recognition_of_priors: Optional[str] = None
    visa_requirement: Optional[str] = None


class FAQ(BaseModel):
    """Frequently asked question."""

    q: str
    a: str


class Program(BaseModel):
    """Complete program information."""

    code: str
    title: str
    degree_level: str  # "bachelor", "master", "doctoral"
    faculty: str
    language_of_instruction: str
    duration_semesters: int
    ects_total: int
    field_of_study: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    intakes: List[Intake]
    application_portal: Optional[ApplicationPortal] = None
    contacts: Optional[Contacts] = None
    eligibility: Optional[Eligibility] = None
    fees: Optional[Fees] = None
    required_documents: Optional[RequiredDocuments] = None
    policies: Optional[Policies] = None
    faqs: Optional[List[FAQ]] = Field(default_factory=list)
    notes: Optional[List[str]] = Field(default_factory=list)
    common_queries: Optional[List[str]] = Field(default_factory=list)
    quick_facts: Optional[List[str]] = Field(default_factory=list)

    def to_context_string(self) -> str:
        """Convert program to a comprehensive formatted string for LLM context."""
        # Convert the entire model to a dictionary to include ALL fields
        data_dict = self.model_dump(exclude_none=True)

        # Helper to format dictionary recursively
        def format_dict(d, indent=0):
            lines = []
            prefix = "  " * indent
            for k, v in d.items():
                key_str = k.replace("_", " ").title()
                if isinstance(v, dict):
                    lines.append(f"{prefix}{key_str}:")
                    lines.extend(format_dict(v, indent + 1))
                elif isinstance(v, list):
                    lines.append(f"{prefix}{key_str}:")
                    for item in v:
                        if isinstance(item, dict):
                            lines.extend(format_dict(item, indent + 1))
                            lines.append(f"{prefix}  ---")
                        else:
                            lines.append(f"{prefix}  - {item}")
                else:
                    lines.append(f"{prefix}{key_str}: {v}")
            return lines

        # Generate formatted string
        formatted_lines = format_dict(data_dict)
        return "\n".join(formatted_lines)


class ProgramMetadata(BaseModel):
    """Metadata wrapper for program YAML files."""

    version: str
    updated_at: str
    program: Program


# Conversation Context Models


class Message(BaseModel):
    """A single message in the conversation."""

    role: str  # "user" or "assistant"
    content: str
    language: str  # "en" or "de"
    timestamp: datetime = Field(default_factory=datetime.now)


class ConversationContext(BaseModel):
    """Conversation context tracking."""

    messages: List[Message] = Field(default_factory=list)
    current_language: str = "en"
    referenced_programs: List[str] = Field(default_factory=list)  # Program codes

    def add_message(self, role: str, content: str, language: str):
        """Add a message to the conversation."""
        self.messages.append(Message(role=role, content=content, language=language))
        self.current_language = language

    def get_recent_messages(self, n: int = 10) -> List[Message]:
        """Get the n most recent messages."""
        return self.messages[-n:]

    def clear(self):
        """Clear conversation history."""
        self.messages.clear()
        self.referenced_programs.clear()

    def to_prompt_context(self, n: int = 5) -> str:
        """Format recent messages for LLM prompt."""
        recent = self.get_recent_messages(n * 2)  # n exchanges = 2n messages
        context = ""
        for msg in recent:
            context += f"{msg.role.capitalize()}: {msg.content}\n"
        return context
