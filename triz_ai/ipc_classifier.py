"""IPC classifier module.

This module provides a high‑level wrapper around the basic IPC
classification defined in :mod:`triz_system`.  It exposes a
`classify_ipc` function that returns a ranked list of IPC codes based
on supplied keywords.  If the underlying mapping does not contain any
entries for the given keywords, it proposes a generic set of top codes
as suggestions.  In a production system this module would interface
with a machine learning model or external API to achieve ≥85% accuracy
on large datasets (see requirement F1).
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional, Tuple

from triz_system import classify_ipc as _base_classify_ipc


def classify_ipc(
    keywords: List[str],
    ipc_mapping: Optional[Dict[str, List[str]]] = None,
    classifier_fn: Optional[Callable[[List[str]], List[str]]] = None,
    top_n: int = 3,
) -> List[str]:
    """Classify invention keywords into IPC codes with suggestions.

    This function delegates to the base implementation in
    :func:`triz_system.classify_ipc` to produce an initial list of IPC
    codes.  If no codes are returned, it falls back to a predefined
    list of generic IPC sections (A–H) and returns the first ``top_n``
    codes.  The caller may supply a custom mapping or classifier
    function to override the default logic.

    Parameters
    ----------
    keywords : list of str
        Keywords extracted from the invention description.
    ipc_mapping : dict, optional
        Custom mapping from keywords to IPC codes.
    classifier_fn : callable, optional
        Alternative classifier that takes a list of keywords and
        returns a list of IPC codes.
    top_n : int, optional
        Maximum number of codes to return.  Defaults to 3.

    Returns
    -------
    list of str
        A ranked list of IPC codes.  If fewer than ``top_n`` codes are
        available, the list will be shorter.
    """
    if classifier_fn is not None:
        codes = classifier_fn(keywords)
    else:
        codes = _base_classify_ipc(keywords, ipc_mapping=ipc_mapping)
    # Deduplicate and limit
    codes = list(dict.fromkeys(codes))  # preserve order
    if codes:
        return codes[:top_n]
    # Fallback suggestions if no codes found: propose generic sections
    generic_suggestions = [
        "A01B",  # Human necessities; agriculture
        "B60R",  # Transporting; vehicles
        "C07D",  # Organic chemistry
        "F16H",  # Mechanical engineering
        "H01L",  # Semiconductor devices
    ]
    return generic_suggestions[:top_n]