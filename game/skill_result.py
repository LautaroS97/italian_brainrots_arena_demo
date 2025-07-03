from dataclasses import dataclass, field
from typing import List

@dataclass
class SkillResult:
    damage: int = 0
    energy_cost: int = 0
    self_damage: int = 0
    pp_steal: int = 0
    states_applied: List[str] = field(default_factory=list)
    state_scope: str = "persistent"
    nullify: bool = False
    blocked: bool = False