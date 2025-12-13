"""Response caching system for instant answers to common queries."""

import logging
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path

try:
    from diskcache import Cache

    DISKCACHE_AVAILABLE = True
except ImportError:
    DISKCACHE_AVAILABLE = False
    logging.warning("diskcache not available, using in-memory cache only")

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    query: str
    query_hash: str
    response: str
    language: str
    timestamp: datetime
    hit_count: int = 0
    ttl: int = 3600  # Time to live in seconds
    programs_referenced: List[str] = field(default_factory=list)

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        age = (datetime.now() - self.timestamp).total_seconds()
        return age > self.ttl

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "query": self.query,
            "query_hash": self.query_hash,
            "response": self.response,
            "language": self.language,
            "timestamp": self.timestamp.isoformat(),
            "hit_count": self.hit_count,
            "ttl": self.ttl,
            "programs_referenced": self.programs_referenced,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CacheEntry":
        """Create from dictionary."""
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class ResponseCache:
    """Cache for storing and retrieving common query responses."""

    def __init__(
        self,
        cache_dir: str = "data/cache",
        max_cache_size: int = 1000,
        default_ttl: int = 3600,
        similarity_threshold: float = 0.85,
        enable_semantic_matching: bool = True,
        embedder: Optional[Any] = None,
    ):
        """
        Initialize response cache.

        Args:
            cache_dir: Directory for persistent cache storage
            max_cache_size: Maximum number of entries to cache
            default_ttl: Default time-to-live in seconds (1 hour)
            similarity_threshold: Minimum similarity for cache hit (0-1)
            enable_semantic_matching: Use embeddings for similarity matching
            embedder: Optional existing sentence transformer instance
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.max_cache_size = max_cache_size
        self.default_ttl = default_ttl
        self.similarity_threshold = similarity_threshold
        self.enable_semantic_matching = enable_semantic_matching

        # Initialize disk cache if available
        if DISKCACHE_AVAILABLE:
            self.disk_cache = Cache(str(self.cache_dir / "responses"))
            logger.info(f"Disk cache initialized at {self.cache_dir}")
        else:
            self.disk_cache = None
            logger.warning("Disk cache not available, using memory only")

        # In-memory cache for fast access
        self.memory_cache: Dict[str, CacheEntry] = {}

        # Cache statistics
        self.stats = {"hits": 0, "misses": 0, "total_queries": 0, "cache_size": 0}

        # Load embedder for semantic matching if enabled
        self.embedder = embedder
        if self.enable_semantic_matching and self.embedder is None:
            self._initialize_embedder()
        elif self.embedder:
            logger.info("Using shared embedder for cache")

        # Load existing cache from disk
        self._load_cache()

    def _initialize_embedder(self):
        """Initialize sentence embedder for semantic matching."""
        try:
            from sentence_transformers import SentenceTransformer

            self.embedder = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            logger.info("Semantic matching enabled for cache")
        except Exception as e:
            logger.warning(
                f"Could not initialize embedder: {e}, using exact matching only"
            )
            self.enable_semantic_matching = False

    def _load_cache(self):
        """Load cache entries from disk."""
        if not self.disk_cache:
            return

        try:
            # Load all entries from disk cache
            for key in self.disk_cache:
                try:
                    entry_dict = self.disk_cache[key]
                    entry = CacheEntry.from_dict(entry_dict)

                    # Skip expired entries
                    if not entry.is_expired():
                        self.memory_cache[key] = entry
                except Exception as e:
                    logger.error(f"Error loading cache entry {key}: {e}")

            self.stats["cache_size"] = len(self.memory_cache)
            logger.info(f"Loaded {len(self.memory_cache)} cache entries from disk")
        except Exception as e:
            logger.error(f"Error loading cache: {e}")

    def _compute_query_hash(self, query: str, language: str) -> str:
        """Compute hash for query."""
        # Normalize query
        normalized = query.lower().strip()
        combined = f"{normalized}:{language}"
        return hashlib.md5(combined.encode()).hexdigest()

    def compute_query_similarity(self, query1: str, query2: str) -> float:
        """
        Compute semantic similarity between two queries.

        Args:
            query1: First query
            query2: Second query

        Returns:
            Similarity score (0-1)
        """
        if not self.enable_semantic_matching or not self.embedder:
            # Fallback to simple string matching
            q1 = query1.lower().strip()
            q2 = query2.lower().strip()
            if q1 == q2:
                return 1.0
            # Simple word overlap
            words1 = set(q1.split())
            words2 = set(q2.split())
            if not words1 or not words2:
                return 0.0
            overlap = len(words1 & words2)
            return overlap / max(len(words1), len(words2))

        try:
            # Use embeddings for semantic similarity
            embeddings = self.embedder.encode([query1, query2])
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            return float(similarity)
        except Exception as e:
            logger.error(f"Similarity computation failed: {e}")
            return 0.0

    def get_cached_response(self, query: str, language: str) -> Optional[str]:
        """
        Get cached response for a query.

        Args:
            query: User query
            language: Language code

        Returns:
            Cached response or None if not found
        """
        self.stats["total_queries"] += 1

        # Try exact match first
        query_hash = self._compute_query_hash(query, language)

        if query_hash in self.memory_cache:
            entry = self.memory_cache[query_hash]

            # Check if expired
            if entry.is_expired():
                logger.debug(f"Cache entry expired: {query[:50]}")
                del self.memory_cache[query_hash]
                if self.disk_cache:
                    del self.disk_cache[query_hash]
                self.stats["misses"] += 1
                return None

            # Cache hit!
            entry.hit_count += 1
            self.stats["hits"] += 1

            logger.info(
                f"Cache HIT (exact): {query[:50]}... (hit_count={entry.hit_count})"
            )

            # Update in disk cache
            if self.disk_cache:
                self.disk_cache[query_hash] = entry.to_dict()

            return entry.response

        # Try semantic matching if enabled
        if self.enable_semantic_matching and self.embedder:
            best_match = None
            best_similarity = 0.0

            for entry in self.memory_cache.values():
                # Only match same language
                if entry.language != language:
                    continue

                # Skip expired
                if entry.is_expired():
                    continue

                similarity = self.compute_query_similarity(query, entry.query)

                if (
                    similarity > best_similarity
                    and similarity >= self.similarity_threshold
                ):
                    best_similarity = similarity
                    best_match = entry

            if best_match:
                best_match.hit_count += 1
                self.stats["hits"] += 1

                logger.info(
                    f"Cache HIT (semantic, {best_similarity:.2f}): {query[:50]}..."
                )

                # Update in disk cache
                if self.disk_cache:
                    match_hash = self._compute_query_hash(
                        best_match.query, best_match.language
                    )
                    self.disk_cache[match_hash] = best_match.to_dict()

                return best_match.response

        # Cache miss
        self.stats["misses"] += 1
        logger.debug(f"Cache MISS: {query[:50]}...")
        return None

    def cache_response(
        self,
        query: str,
        language: str,
        response: str,
        ttl: int = None,
        programs_referenced: List[str] = None,
    ) -> None:
        """
        Cache a response.

        Args:
            query: User query
            language: Language code
            response: Response to cache
            ttl: Time to live in seconds (optional)
            programs_referenced: List of program codes referenced (optional)
        """
        query_hash = self._compute_query_hash(query, language)

        # Check cache size limit
        if len(self.memory_cache) >= self.max_cache_size:
            self._evict_lru()

        # Create cache entry
        entry = CacheEntry(
            query=query,
            query_hash=query_hash,
            response=response,
            language=language,
            timestamp=datetime.now(),
            hit_count=0,
            ttl=ttl or self.default_ttl,
            programs_referenced=programs_referenced or [],
        )

        # Store in memory
        self.memory_cache[query_hash] = entry

        # Store in disk cache
        if self.disk_cache:
            self.disk_cache[query_hash] = entry.to_dict()

        self.stats["cache_size"] = len(self.memory_cache)

        logger.debug(f"Cached response: {query[:50]}...")

    def _evict_lru(self):
        """Evict least recently used entry."""
        if not self.memory_cache:
            return

        # Find entry with lowest hit count and oldest timestamp
        lru_key = min(
            self.memory_cache.keys(),
            key=lambda k: (
                self.memory_cache[k].hit_count,
                self.memory_cache[k].timestamp,
            ),
        )

        logger.debug(f"Evicting LRU entry: {self.memory_cache[lru_key].query[:50]}...")

        del self.memory_cache[lru_key]
        if self.disk_cache and lru_key in self.disk_cache:
            del self.disk_cache[lru_key]

    def invalidate_cache(self, pattern: str = None) -> int:
        """
        Invalidate cache entries matching pattern.

        Args:
            pattern: Pattern to match (None = clear all)

        Returns:
            Number of entries invalidated
        """
        if pattern is None:
            # Clear all
            count = len(self.memory_cache)
            self.memory_cache.clear()
            if self.disk_cache:
                self.disk_cache.clear()
            self.stats["cache_size"] = 0
            logger.info(f"Cleared all cache ({count} entries)")
            return count

        # Match pattern in queries
        to_remove = []
        for key, entry in self.memory_cache.items():
            if pattern.lower() in entry.query.lower():
                to_remove.append(key)

        # Remove matched entries
        for key in to_remove:
            del self.memory_cache[key]
            if self.disk_cache and key in self.disk_cache:
                del self.disk_cache[key]

        self.stats["cache_size"] = len(self.memory_cache)
        logger.info(f"Invalidated {len(to_remove)} cache entries matching '{pattern}'")

        return len(to_remove)

    def clear_old_entries(self, max_age: int = 86400) -> int:
        """
        Clear entries older than max_age.

        Args:
            max_age: Maximum age in seconds (default: 24 hours)

        Returns:
            Number of entries cleared
        """
        cutoff = datetime.now() - timedelta(seconds=max_age)
        to_remove = []

        for key, entry in self.memory_cache.items():
            if entry.timestamp < cutoff:
                to_remove.append(key)

        for key in to_remove:
            del self.memory_cache[key]
            if self.disk_cache and key in self.disk_cache:
                del self.disk_cache[key]

        self.stats["cache_size"] = len(self.memory_cache)
        logger.info(f"Cleared {len(to_remove)} old cache entries")

        return len(to_remove)

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        hit_rate = 0.0
        if self.stats["total_queries"] > 0:
            hit_rate = self.stats["hits"] / self.stats["total_queries"]

        return {
            "total_queries": self.stats["total_queries"],
            "cache_hits": self.stats["hits"],
            "cache_misses": self.stats["misses"],
            "hit_rate": hit_rate,
            "cache_size": len(self.memory_cache),
            "max_cache_size": self.max_cache_size,
            "semantic_matching_enabled": self.enable_semantic_matching,
        }
