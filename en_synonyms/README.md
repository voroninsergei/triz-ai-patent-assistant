# en_synonyms

Lightweight English synonyms provider mirroring the `ru_synonyms` API.

- Primary source: **NLTK WordNet** (optional at runtime).
- Fallback: a tiny built-in adjacency list in `_data/synonyms.adjlist` so the API
  remains usable without NLTK data.

## Usage

```python
from en_synonyms import SynonymsGraph

g = SynonymsGraph()  # will use WordNet if available, otherwise fallback
print(list(g.get_list("device")))         # immediate synonyms
print(list(g.get_list_in_radius("device", radius=2)))  # wider neighborhood
```

## Integration tip

If your code currently uses NLTK WordNet directly for English, you can switch to
this package for a unified API with `ru_synonyms`:

```python
# before
# from nltk.corpus import wordnet

# after
from en_synonyms import SynonymsGraph as ENSynonymsGraph
EN_SYNS = ENSynonymsGraph()
# EN_SYNS.get_list("device")
```

## Optional dependency

The package tries to import `nltk.corpus.wordnet` at runtime. If NLTK is not
installed or WordNet data is unavailable, the graph will still work (using
`_data/synonyms.adjlist`), just with a much smaller vocabulary.
