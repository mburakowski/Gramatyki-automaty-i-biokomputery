"""
Allows selecting a target regular language by name.

Each language lives in a module under "languages/" and must define:
    NAME, ALPHABET, DEFAULT_MAX_LEN, teacher_dfa().
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class LanguageSpec:
    """structure for a language module."""

    name: str
    module: str

# All added languages. 
LANGUAGES: List[LanguageSpec] = [
    LanguageSpec("even_a", "languages.even_a"),
    LanguageSpec("ends_with_ab", "languages.ends_with_ab"),
    LanguageSpec("contains_aa", "languages.contains_aa"),
    LanguageSpec("no_bb", "languages.no_bb"),
    LanguageSpec("mod3_a", "languages.mod3_a"),
]


def list_languages() -> List[str]:
    """Returns all registered language names."""
    return [s.name for s in LANGUAGES]


def get_language(name: str) -> Any:
    """Loads and returns the language module by name."""
    name = name.strip()
    for spec in LANGUAGES:
        if spec.name == name:
            return importlib.import_module(spec.module)
    raise ValueError(
        f"Unknown language: {name!r}. Available: {', '.join(list_languages())}"
    )
