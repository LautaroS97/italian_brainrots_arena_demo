from typing import Callable, List, Optional, Tuple
from game.skill_result import SkillResult
from game.battle_event import BattleEvent
from constants import COLOR_PP, COLOR_HP


class Skill:
    def __init__(
        self,
        name: str,
        description: str,
        energy_cost: int,
        execute: Optional[Callable] = None,
        *,
        execute_fn: Optional[Callable] = None,
        animation: Optional[dict] = None,
        priority: bool = False,
        is_direct_attack: bool = True,
        is_defense: bool = False,
        render_behind_rival: bool = False,
        extra_message: Optional[Callable | str] = None,
    ):
        self.name = name
        self.description = description
        self.energy_cost = energy_cost
        self.execute_fn = execute_fn or execute
        if self.execute_fn is None:
            raise ValueError("Skill necesita una función de ejecución.")
        self.animation = animation or {}
        self.priority = priority
        self.is_direct_attack = is_direct_attack
        self.is_defense = is_defense
        self.render_behind_rival = render_behind_rival
        self.extra_message = extra_message

    def execute(self, attacker, defender) -> Tuple[SkillResult, List[BattleEvent]]:
        events: List[BattleEvent] = []
        cost = int(self.energy_cost * attacker.next_energy_mult)
        attacker.next_energy_mult = 1.0
        attacker.consume_energy(cost)
        events.append(BattleEvent("skill", f"{attacker.name} usó {self.name}."))

        if not self.is_defense:
            events.append(BattleEvent("cost", f"Consumió {cost} PP.", COLOR_PP))

        try:
            result: SkillResult = self.execute_fn(attacker, defender, cost)
        except TypeError:
            result = self.execute_fn(attacker, defender)

        if result.damage > 0:
            events.append(BattleEvent("damage", f"Causó {result.damage} de daño.", COLOR_HP))
        elif not self.is_defense:
            events.append(BattleEvent("info", "Es un movimiento defensivo."))

        for st in result.states_applied:
            events.append(BattleEvent("info", f"{defender.name} adquirió {st}."))

        if result.state_scope == "next_move" and result.states_applied:
            events.append(BattleEvent("info", "Sólo afectará al próximo movimiento."))

        if self.extra_message:
            extra = self.extra_message(attacker, defender) if callable(self.extra_message) else self.extra_message
            if extra:
                events.append(BattleEvent("info", extra))

        if self.is_defense:
            events.append(BattleEvent("cost", f"Consumió {cost} PP.", COLOR_PP))

        result.energy_cost = cost
        return result, events