"""
Each language module exposes:
    NAME: str
    ALPHABET: tuple[str, ...]
    DEFAULT_MAX_LEN: int
    teacher_dfa() -> DFA

This package provides a small registry for dynamic loading.
"""

from .registry import get_language, list_languages

__all__ = ["get_language", "list_languages"]
