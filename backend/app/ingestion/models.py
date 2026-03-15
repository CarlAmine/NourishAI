from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class DocumentChunk:
    chunk_id: str
    doc_id: str
    doc_type: str
    text: str
    payload: Dict[str, Any]
