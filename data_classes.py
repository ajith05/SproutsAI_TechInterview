from dataclasses import dataclass
from typing import List, Tuple

# ──────────────── payload dataclasses ────────────────
@dataclass
class NLQuery:
    question: str

@dataclass
class SQLText:
    sql: str

@dataclass
class SQLResult:
    rows: List[Tuple]          # list[tuple[Any, …]]

@dataclass
class FinalAnswer:
    answer: str
# ─────────────────────────────────────────────────────
