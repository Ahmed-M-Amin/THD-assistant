"""Program data store for loading and managing YAML program data."""

import yaml
import logging
import numpy as np
from pathlib import Path
from typing import List, Optional, Dict
from pydantic import ValidationError
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from src.models import Program, ProgramMetadata

logger = logging.getLogger(__name__)


class ProgramDataStore:
    """Manages loading and accessing program data from YAML files."""

    def __init__(
        self, data_path: str = "data/programs", enable_semantic_search: bool = True
    ):
        """
        Initialize the data store.

        Args:
            data_path: Path to directory containing program YAML files
            enable_semantic_search: Whether to load embedding model for semantic search
        """
        self.data_path = Path(data_path)
        self.programs: List[Program] = []
        self.programs_by_code: Dict[str, Program] = {}
        self.programs_by_level: Dict[str, List[Program]] = {
            "bachelor": [],
            "master": [],
            "doctoral": [],
        }

        # Semantic search components
        self.enable_semantic_search = enable_semantic_search
        self.embedder: Optional[SentenceTransformer] = None
        self.program_embeddings: Optional[np.ndarray] = None
        self.embedding_texts: List[str] = []

        self._load_programs()

        if self.enable_semantic_search and self.programs:
            self._initialize_embeddings()

    def _load_programs(self):
        """Load all program YAML files from the data directory."""
        if not self.data_path.exists():
            logger.error(f"Data path does not exist: {self.data_path}")
            return

        yaml_files = list(self.data_path.glob("*.yaml")) + list(
            self.data_path.glob("*.yml")
        )

        if not yaml_files:
            logger.warning(f"No YAML files found in {self.data_path}")
            return

        logger.info(f"Loading {len(yaml_files)} program files...")

        for yaml_file in yaml_files:
            # Skip content_index.yaml (index file) - robust check
            if "content_index" in yaml_file.name.lower():
                logger.debug(f"Skipping index file: {yaml_file.name}")
                continue

            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                # Parse with Pydantic
                program_metadata = ProgramMetadata(**data)
                program = program_metadata.program

                # Add to collections
                self.programs.append(program)
                self.programs_by_code[program.code] = program

                # Index by degree level
                if program.degree_level in self.programs_by_level:
                    self.programs_by_level[program.degree_level].append(program)

                logger.debug(f"Loaded program: {program.title} ({program.code})")

            except ValidationError as e:
                logger.error(f"Validation error in {yaml_file.name}: {e}")
            except yaml.YAMLError as e:
                logger.error(f"YAML parse error in {yaml_file.name}: {e}")
            except Exception as e:
                logger.error(f"Error loading {yaml_file.name}: {e}")

        logger.info(f"Successfully loaded {len(self.programs)} programs")

    def get_program_by_code(self, code: str) -> Optional[Program]:
        """
        Get a program by its code.

        Args:
            code: Program code (e.g., "bsc_ai")

        Returns:
            Program object or None if not found
        """
        return self.programs_by_code.get(code)

    def get_programs_by_level(self, level: str) -> List[Program]:
        """
        Get all programs of a specific degree level.

        Args:
            level: Degree level ("bachelor", "master", or "doctoral")

        Returns:
            List of programs
        """
        return self.programs_by_level.get(level, [])

    def search_by_title(self, query: str) -> List[Program]:
        """
        Search programs by title (case-insensitive substring match).

        Args:
            query: Search query

        Returns:
            List of matching programs
        """
        query_lower = query.lower()
        return [p for p in self.programs if query_lower in p.title.lower()]

    def get_all_programs(self) -> List[Program]:
        """Get all loaded programs."""
        return self.programs

    def get_program_count(self) -> int:
        """Get total number of loaded programs."""
        return len(self.programs)

    def get_programs_by_language(self, language: str) -> List[Program]:
        """
        Get programs by language of instruction.

        Args:
            language: Language code (e.g., "en", "de")

        Returns:
            List of programs
        """
        return [p for p in self.programs if p.language_of_instruction == language]

    def reload(self):
        """Reload all program data from disk."""
        self.programs.clear()
        self.programs_by_code.clear()
        for level in self.programs_by_level:
            self.programs_by_level[level].clear()
        self._load_programs()

        if self.enable_semantic_search and self.programs:
            self._initialize_embeddings()

    def _initialize_embeddings(self):
        """Initialize the embedding model and create embeddings for all programs."""
        try:
            logger.info("Loading sentence transformer model for semantic search...")
            self.embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

            # Create text representations for each program
            self.embedding_texts = []
            for program in self.programs:
                # Combine multiple fields for richer semantic representation
                text = f"{program.title} {program.code} {program.degree_level} {program.faculty}"

                # Add language info
                text += f" language:{program.language_of_instruction}"

                # Add key eligibility info if available
                if program.eligibility:
                    if program.eligibility.language_requirements:
                        if program.eligibility.language_requirements.german:
                            text += f" german:{program.eligibility.language_requirements.german.minimum_level}"
                        if program.eligibility.language_requirements.english:
                            text += f" english:{program.eligibility.language_requirements.english.minimum_level}"

                    # Add academic background requirements
                    if program.eligibility.academic_background:
                        if program.eligibility.academic_background.bachelor:
                            text += f" bachelor_req:{' '.join(str(v) for v in program.eligibility.academic_background.bachelor.values())}"
                        if program.eligibility.academic_background.master:
                            text += f" master_req:{' '.join(str(v) for v in program.eligibility.academic_background.master.values())}"

                # Add fees information
                if program.fees:
                    text += " fees tuition cost price"
                    if program.fees.domestic_german:
                        text += f" domestic:{program.fees.domestic_german.tuition_per_semester}"
                    if program.fees.international_non_eu:
                        text += f" international:{program.fees.international_non_eu.tuition_per_semester} {program.fees.international_non_eu.service_fee_per_semester}"

                # Add intake and deadline information
                if program.intakes:
                    text += " deadline application date"
                    for intake in program.intakes:
                        text += f" {intake.term}:{intake.application_window.start}-{intake.application_window.end}"

                self.embedding_texts.append(text)

            # Generate embeddings
            logger.info(
                f"Generating embeddings for {len(self.embedding_texts)} programs..."
            )
            self.program_embeddings = self.embedder.encode(
                self.embedding_texts, show_progress_bar=False, convert_to_numpy=True
            )

            logger.info("Semantic search initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize semantic search: {e}")
            self.enable_semantic_search = False
            self.embedder = None
            self.program_embeddings = None

    def semantic_search(
        self, query: str, top_k: int = 3, threshold: float = 0.0
    ) -> List[Program]:
        """
        Perform semantic search for programs matching the query.

        Args:
            query: Search query in natural language
            top_k: Number of top results to return
            threshold: Minimum similarity score (0-1)

        Returns:
            List of programs ranked by relevance
        """
        if not self.enable_semantic_search or self.embedder is None:
            logger.warning(
                "Semantic search not available, falling back to title search"
            )
            return self.search_by_title(query)

        try:
            # Encode query
            query_embedding = self.embedder.encode([query], convert_to_numpy=True)

            # Calculate similarities
            similarities = cosine_similarity(query_embedding, self.program_embeddings)[
                0
            ]

            # Get top-k indices above threshold
            top_indices = np.argsort(similarities)[::-1][:top_k]

            results = []
            for idx in top_indices:
                if similarities[idx] >= threshold:
                    results.append(self.programs[idx])
                    logger.debug(
                        f"Match: {self.programs[idx].title} (score: {similarities[idx]:.3f})"
                    )

            return results

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return self.search_by_title(query)

    def semantic_search_on_programs(
        self, query: str, programs: List[Program], top_k: int = 3
    ) -> List[Program]:
        """
        Perform semantic search on a specific subset of programs.

        Args:
            query: Search query in natural language
            programs: Subset of programs to search within
            top_k: Number of top results to return

        Returns:
            List of programs ranked by relevance
        """
        if not programs:
            return []

        if not self.enable_semantic_search or self.embedder is None:
            logger.warning("Semantic search not available")
            return programs[:top_k]

        try:
            # Encode query
            query_embedding = self.embedder.encode([query], convert_to_numpy=True)

            # Get embeddings for the filtered programs
            program_indices = [
                self.programs.index(p) for p in programs if p in self.programs
            ]
            subset_embeddings = self.program_embeddings[program_indices]

            # Calculate similarities
            similarities = cosine_similarity(query_embedding, subset_embeddings)[0]

            # Get top-k indices
            top_indices = np.argsort(similarities)[::-1][:top_k]

            results = []
            for idx in top_indices:
                program = programs[idx]
                results.append(program)
                logger.debug(f"Match: {program.title} (score: {similarities[idx]:.3f})")

            return results

        except Exception as e:
            logger.error(f"Semantic search on programs failed: {e}")
            return programs[:top_k]

    def find_relevant_programs(self, query: str, max_results: int = 3) -> List[Program]:
        """
        Find programs relevant to a user query using semantic search.

        This is the main method to use for RAG context retrieval.

        Args:
            query: User's natural language query
            max_results: Maximum number of programs to return

        Returns:
            List of relevant programs
        """
        return self.semantic_search(query, top_k=max_results, threshold=0.1)
