from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class BattleEvent:
    kind: str
    text: str
    color: Optional[Tuple[int, int, int]] = None