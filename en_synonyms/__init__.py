"""English synonyms package exposing a SynonymsGraph.

This module mirrors the public API of ru_synonyms by providing a
`SynonymsGraph` that can return lists of synonyms for a given word.
It automatically loads an offline thesaurus from `en_thesaurus.jsonl` if
present, and optionally expands the graph on demand using NLTK WordNet.
"""

from .synonyms import SynonymsGraph

__all__ = ["SynonymsGraph"]