import random

class StatusEffect:
    def __init__(self, name, icon_path, cure_chance=0.5):
        self.name = name
        self.icon_path = icon_path
        self.cure_chance = cure_chance
        self.cured = False
    def on_damage_calc(self, dmg):
        return dmg
    def on_energy_calc(self, cost):
        return cost
    def apply_effect(self, target):
        pass
    def tick_effect(self, target):
        pass
    def try_cure(self):
        if random.random() < self.cure_chance:
            self.cured = True

class Radiacion(StatusEffect):
    def __init__(self):
        super().__init__("Radiación", "assets/icons/radiacion.png", 0.5)
    def tick_effect(self, target):
        target.hp = max(0, target.hp - 5)

class Mojado(StatusEffect):
    def __init__(self):
        super().__init__("Mojado", "assets/icons/mojado.png", 0.5)
    def apply_effect(self, target):
        target.pp_multiplier *= 1.05

class Mareado(StatusEffect):
    def __init__(self):
        super().__init__("Mareado", "assets/icons/mareado.png", 0.5)
    def apply_effect(self, target):
        target.damage_multiplier *= 0.4

class Veneno(StatusEffect):
    def __init__(self):
        super().__init__("Veneno", "assets/icons/veneno.png", 0.5)
    def tick_effect(self, target):
        target.hp = max(0, target.hp - 10)
        target.energy = max(0, target.energy - 5)
        target.damage_multiplier *= 0.9
        target.pp_multiplier *= 1.1

class NextMoveEffect(StatusEffect):
    def __init__(self, name, icon_path):
        super().__init__(name, icon_path, 1.0)
    def tick_effect(self, target):
        self.cured = True

class Debilitado20(NextMoveEffect):
    def __init__(self):
        super().__init__("Debilitado 20%", "assets/icons/debilitado20.png")
    def apply_effect(self, target):
        target.pending_effects["damage_mod"] = 0.8

class Debilitado50(NextMoveEffect):
    def __init__(self):
        super().__init__("Debilitado 50%", "assets/icons/debilitado50.png")
    def apply_effect(self, target):
        target.pending_effects["damage_mod"] = 0.5

class Debilitado75(NextMoveEffect):
    def __init__(self):
        super().__init__("Debilitado 75%", "assets/icons/debilitado75.png")
    def apply_effect(self, target):
        target.pending_effects["damage_mod"] = 0.25

class EnergyUp25(NextMoveEffect):
    def __init__(self):
        super().__init__("PP +25%", "assets/icons/energyup25.png")
    def apply_effect(self, target):
        target.pending_effects["energy_mod"] = 1.25

class NullifyNextAttack(NextMoveEffect):
    def __init__(self):
        super().__init__("Anulado", "assets/icons/nullify.png")
    def apply_effect(self, target):
        target.pending_effects["nullify"] = True