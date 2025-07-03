import random
from game.skill_result import SkillResult
from game.status_effects import (
    Radiacion,
    Mojado,
    Mareado,
    Veneno,
    Debilitado20,
    Debilitado50,
    Debilitado75,
    EnergyUp25,
    NullifyNextAttack,
)

def deal_damage(min_dmg: int, max_dmg: int):
    def fn(attacker, defender):
        amount = random.randint(min_dmg, max_dmg)
        defender.take_damage(amount)
        return SkillResult(damage=amount)
    return fn

def steal_health(min_dmg: int, max_dmg: int):
    def fn(attacker, defender):
        amount = random.randint(min_dmg, max_dmg)
        defender.take_damage(amount)
        healed = attacker.heal(amount)
        return SkillResult(damage=amount, self_damage=-healed)
    return fn

def steal_energy(amount: int):
    def fn(attacker, defender):
        stolen = min(defender.energy, amount)
        defender.energy -= stolen
        attacker.restore_energy(stolen)
        return SkillResult(pp_steal=stolen)
    return fn

def drain_energy(amount: int):
    def fn(attacker, defender):
        stolen = min(defender.energy, amount)
        defender.energy -= stolen
        attacker.restore_energy(stolen)
        return SkillResult(pp_steal=stolen)
    return fn

def heal(amount: int):
    def fn(attacker, defender):
        healed = attacker.heal(amount)
        return SkillResult(self_damage=-healed)
    return fn

def restore_energy(amount: int):
    def fn(attacker, defender):
        gained = attacker.restore_energy(amount)
        return SkillResult(pp_steal=-gained)
    return fn

def skip_turn():
    def fn(attacker, defender):
        defender.pending_effects["skip_turn"] = True
        return SkillResult(state_scope="next_move")
    return fn

def _add_state(defender, status_cls, scope):
    if not any(isinstance(s, status_cls) for s in defender.status_effects):
        status = status_cls()
        defender.add_status(status)
        return status.name
    return None

def deal_damage_with_status(min_dmg: int, max_dmg: int, status_cls):
    def fn(attacker, defender):
        amount = random.randint(min_dmg, max_dmg)
        defender.take_damage(amount)
        st = _add_state(defender, status_cls, "persistent")
        names = [st] if st else []
        return SkillResult(damage=amount, states_applied=names)
    return fn

def deal_damage_with_status_both(min_dmg: int, max_dmg: int, status_cls):
    def fn(attacker, defender):
        amount = random.randint(min_dmg, max_dmg)
        defender.take_damage(amount)
        _add_state(defender, status_cls, "persistent")
        _add_state(attacker, status_cls, "persistent")
        return SkillResult(damage=amount, states_applied=[status_cls.__name__])
    return fn

def weaken_next_attack(mult: float):
    def fn(attacker, defender):
        if mult <= 0.25:
            defender.add_status(Debilitado75())
            label = "Debilitado 75%"
        elif mult <= 0.5:
            defender.add_status(Debilitado50())
            label = "Debilitado 50%"
        else:
            defender.add_status(Debilitado20())
            label = "Debilitado 20%"
        return SkillResult(states_applied=[label], state_scope="next_move")
    return fn

def raise_defense_nullify():
    def fn(attacker, defender):
        attacker.nullify_next_attack = True
        return SkillResult(states_applied=["Anulado"], state_scope="next_move")
    return fn

def extra_energy_cost(factor: float):
    def fn(attacker, defender):
        defender.add_status(EnergyUp25())
        return SkillResult(states_applied=["PP +25%"], state_scope="next_move")
    return fn

def self_damage(amount: int):
    def fn(attacker, defender):
        attacker.take_damage(amount)
        return SkillResult(self_damage=amount)
    return fn

def reflect_damage_if_direct(min_dmg: int, max_dmg: int):
    def fn(attacker, defender):
        attacker.reflect_on_next_direct = (True, min_dmg, max_dmg)
        return SkillResult()
    return fn