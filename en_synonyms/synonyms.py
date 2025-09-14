import networkx as nx
from typing import Iterator, Set
from pathlib import Path

# Import the local abstract interface (copied from ru_synonyms for independence)
from .lexica import LexicalGraphInterface


class SynonymsGraph(LexicalGraphInterface):
    """English synonyms graph.

    - Uses NLTK WordNet when available to expand the graph on demand.
    - Falls back to a small built-in adjacency list for offline use.

    Notes:
        * Nodes are stored lowercased and with spaces (WordNet underscores -> spaces).
        * get_list(...) and get_list_in_radius(...) accept any casing; they normalise.
    """

    def __init__(self, use_wordnet: bool = True, max_lemmas_per_synset: int = 12):
        self._use_wordnet = use_wordnet
        self._wn = None  # lazily imported NLTK wordnet
        self._max_lemmas_per_synset = max_lemmas_per_synset
        super().__init__()

    # ------------------------------------------------------------------
    # Base-class hooks
    # ------------------------------------------------------------------
    def _initialize_graph(self) -> nx.Graph:
        # Seed with a tiny offline graph if available; otherwise start empty.
        graph = nx.Graph()
        adj_path = Path(__file__).parent / "_data" / "synonyms.adjlist"
        if adj_path.exists():
            try:
                graph = nx.read_adjlist(str(adj_path))
            except Exception:
                graph = nx.Graph()
        return graph

    # ------------------------------------------------------------------
    # Public API (mirrors ru_synonyms)
    # ------------------------------------------------------------------
    def get_list(self, word: str) -> Iterator[str]:
        norm = self._normalise(word)
        self._expand_neighborhood(norm, depth=1)
        # Ensure the node exists even if no neighbors were found
        if norm not in self._graph:
            self._graph.add_node(norm)
        return self._graph.neighbors(norm)

    # Backwards-compatibility alias in case callers use get_synonyms(...)
    def get_synonyms(self, word: str) -> Iterator[str]:
        return self.get_list(word)

    def get_list_in_radius(self, word: str, radius: int) -> Iterator[str]:
        if radius > 3:
            raise ValueError(f"Given radius is too big. Maximum value is 3, got radius={radius}.")
        if radius <= 0:
            raise ValueError(f"Given radius must be positive and greater than 0, got radius={radius}.")
        norm = self._normalise(word)
        # Expand neighborhood up to the requested radius so the ego graph has content
        self._expand_neighborhood(norm, depth=radius)
        return nx.ego_graph(self._graph, norm, radius=radius, undirected=True).nodes()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _ensure_wordnet(self) -> None:
        if self._wn is not None or not self._use_wordnet:
            return
        try:
            from nltk.corpus import wordnet as wn  # type: ignore
            self._wn = wn
        except Exception:
            self._wn = None

    @staticmethod
    def _normalise(token: str) -> str:
        return token.strip().replace('_', ' ').lower()

    def _expand_neighborhood(self, seed: str, depth: int = 1) -> None:
        """Expand the graph around *seed* up to *depth* hops using WordNet.

        The expansion is on-demand and cached in the underlying graph.
        """
        if not seed:
            return
        # Always ensure the seed node exists
        if seed not in self._graph:
            self._graph.add_node(seed)

        self._ensure_wordnet()
        if self._wn is None or depth <= 0:
            return

        frontier: Set[str] = {seed}
        seen: Set[str] = set()

        for _ in range(depth):
            next_frontier: Set[str] = set()
            for word in list(frontier):
                if word in seen:
                    continue
                seen.add(word)
                syns: Set[str] = set()
                try:
                    query = word.replace(' ', '_')
                    for syn in self._wn.synsets(query):
                        # Collect lemma names (limit to keep graph small/lightweight)
                        lemmas = [self._normalise(l.name()) for l in syn.lemmas()][: self._max_lemmas_per_synset]
                        syns.update(l for l in lemmas if l and l != word)
                except Exception:
                    pass
                # Connect word <-> each synonym (undirected)
                for s in syns:
                    self._graph.add_edge(word, s)
                next_frontier.update(syns)
            frontier = next_frontier
