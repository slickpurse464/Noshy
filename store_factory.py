"""
Noshy shared store singleton — all modules import from here.
Prevents 5 separate SQLite connections to the same database.
"""
import os
import logging
from typing import Optional

log = logging.getLogger("noshy.store_factory")

_store = None
_embedder = None


def get_store(db_path: str = None, embedder=None):
    """Get or create the shared NoshyStore singleton."""
    global _store, _embedder
    if _store is None or (db_path and _store.db_path != db_path):
        from store import NoshyStore
        if embedder is None:
            _embedder = _detect_embedder()
        else:
            _embedder = embedder
        _store = NoshyStore(db_path=db_path, embedder=_embedder)
        log.debug(f"Shared store initialized: {_store.db_path} (embedder: {type(_embedder).__name__})")
    return _store


def reset_store():
    """Reset the singleton — closes connections and clears reference."""
    global _store, _embedder
    if _store is not None:
        try:
            _store.close()
        except Exception:
            pass
    _store = None
    _embedder = None


def _detect_embedder():
    """Auto-detect the best available embedding provider."""
    from embed import auto_embedder
    return auto_embedder()
