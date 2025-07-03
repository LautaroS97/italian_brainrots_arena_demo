import random
from typing import List
from game.sound_manager import SoundManager
from game.skill import Skill
from game.brainrot import Brainrot
from game.battle_event import BattleEvent
from constants import COLOR_PP, COLOR_HP


class _MsgProxy:
    def __init__(self, sink: List[BattleEvent]):
        self._sink = sink

    def show_message(self, text: str):
        if text:
            self._sink.append(BattleEvent("info", text))


class BattleManager:
    def __init__(
        self,
        player1: Brainrot,
        player2: Brainrot,
        sound_manager: SoundManager | None = None,
    ):
        self.player1 = player1
        self.player2 = player2
        self.turn = 1
        self.events: List[BattleEvent] = [
            BattleEvent("info", f"{self.get_active_player().name} comienza el combate!")
        ]
        self.game_over = False
        self.winner: str | None = None
        self.sound_manager = sound_manager
        self.pending_victory_type: str | None = None

    def get_active_player(self) -> Brainrot:
        return self.player1 if self.turn == 1 else self.player2

    def get_enemy_player(self) -> Brainrot:
        return self.player2 if self.turn == 1 else self.player1

    def apply_action(self, skill: Skill):
        if self.game_over:
            self.events = [BattleEvent("info", "El combate ya ha terminado.")]
            return

        attacker = self.get_active_player()
        defender = self.get_enemy_player()
        events: List[BattleEvent] = []

        attacker._defended_this_turn = False

        skip_turn = attacker.apply_pending_effects(events)
        proxy = _MsgProxy(events)
        attacker.process_statuses(proxy)
        defender.process_statuses(proxy)
        if self._check_immediate_death(attacker, defender, events):
            self.events = events
            return
        if skip_turn:
            self.turn = 2 if self.turn == 1 else 1
            events.append(BattleEvent("info", f"Turno de {self.get_active_player().name}."))
            self.events = events
            return

        if defender.nullify_next_attack:
            defender.nullify_next_attack = False
            cost = int(skill.energy_cost * attacker.next_energy_mult)
            attacker.next_energy_mult = 1.0
            attacker.consume_energy(cost)
            events.append(BattleEvent("skill", f"{attacker.name} usó {skill.name}."))
            events.append(BattleEvent("cost", f"Consumió {cost} PP.", COLOR_PP))
            events.append(BattleEvent("info", "¡Pero el ataque fue anulado!"))
            events.append(BattleEvent("blocked", "El ataque fue bloqueado."))
        else:
            result, skill_events = skill.execute(attacker, defender)
            events.extend(skill_events)
            if result.blocked:
                events.append(BattleEvent("blocked", "El ataque fue bloqueado."))

            if skill.is_direct_attack and getattr(defender, "reflect_on_next_direct", None):
                flag, lo, hi = defender.reflect_on_next_direct
                if flag:
                    reflected = random.randint(lo, hi)
                    attacker.take_damage(reflected)
                    defender.reflect_on_next_direct = (False, 0, 0)
                    events.append(BattleEvent("damage", f"{defender.name} reflejó {reflected} PV.", COLOR_HP))

        defender.resume_freeze()

        self._check_post_action(attacker, defender, events)
        if not self.game_over:
            self.turn = 2 if self.turn == 1 else 1
            events.append(BattleEvent("info", f"Turno de {self.get_active_player().name}."))

        self.events = events

    def _check_immediate_death(
        self, attacker: Brainrot, defender: Brainrot, ev: List[BattleEvent]
    ) -> bool:
        if attacker.is_dead():
            self._set_winner(
                defender, "health", ev, f"{attacker.name} fue derrotado. {defender.name} gana el combate."
            )
            return True
        if defender.is_dead():
            self._set_winner(
                attacker, "health", ev, f"{defender.name} fue derrotado. {attacker.name} gana el combate."
            )
            return True
        return False

    def _check_post_action(
        self, attacker: Brainrot, defender: Brainrot, ev: List[BattleEvent]
    ):
        if attacker.is_dead():
            self._set_winner(
                defender, "health", ev, f"{attacker.name} fue derrotado. {defender.name} gana el combate."
            )
        elif attacker.energy <= 0:
            self._set_winner(
                defender, "energy", ev, f"{attacker.name} se quedó sin energía. {defender.name} gana el combate."
            )
        elif defender.is_dead():
            self._set_winner(
                attacker, "health", ev, f"{defender.name} fue derrotado. {attacker.name} gana el combate."
            )
        elif defender.energy <= 0:
            self._set_winner(
                attacker, "energy", ev, f"{defender.name} se quedó sin energía. {attacker.name} gana el combate."
            )

    def _set_winner(
        self,
        winner_brainrot: Brainrot,
        victory_type: str,
        ev: List[BattleEvent],
        final_msg: str,
    ):
        self.game_over = True
        self.winner = winner_brainrot.name
        self.pending_victory_type = victory_type
        ev.append(BattleEvent("info", final_msg))

    def play_victory_sound(self):
        if not self.game_over or not self.sound_manager:
            return
        winner = self.winner
        loser = self.player1.name if self.player1.name != winner else self.player2.name
        if self.pending_victory_type == "health":
            self.sound_manager.play_victory_health(loser, winner)
        elif self.pending_victory_type == "energy":
            self.sound_manager.play_victory_energy(loser, winner)
        self.pending_victory_type = None

    def is_game_over(self) -> bool:
        return self.game_over

    def get_events(self) -> List[BattleEvent]:
        return self.events

    def start_intro_sequence(self):
        if self.sound_manager:
            self.sound_manager.play_intro_sequence(self.player1.name, self.player2.name)