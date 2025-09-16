"""
en_synonyms abstract class (mirrors ru_synonyms.lexica)
"""
import abc
from typing import Iterator
import networkx as nx


class LexicalGraphInterface(abc.ABC):
    """The LexicalGraphInterface object gives you various lexicas depending on Graph used."""

    def __init__(self):
        self._graph = self._initialize_graph()

    @abc.abstractmethod
    def _initialize_graph(self) -> nx.Graph:
        pass

    def get_list(self, word: str) -> Iterator[str]:
        """Returns list of lexicas for a given word (neighbors in the graph)."""
        return self._graph.neighbors(word)

    def is_in_dictionary(self, word: str) -> bool:
        """Returns whether word is present in the graph."""
        return word in self._graph

    def get_list_in_radius(self, word: str, radius: int) -> Iterator[str]:
        """Returns all words within the given radius in the graph.

        Args:
            word: A word to search near.
            radius: Search radius, 0 < radius <= 3
        """
        if radius > 3:
            raise ValueError(f"Given radius is too big. Maximum value is 3, got radius={radius}.")
        if radius <= 0:
            raise ValueError(f"Given radius must be positive and greater than 0, got radius={radius}.")
        return nx.ego_graph(self._graph, word, radius=radius, undirected=True).nodes()