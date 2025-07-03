import os
import pygame
from typing import Dict
from game.status_effects import StatusEffect
from game.status_texts import STATUS_MESSAGES
from game.battle_event import BattleEvent
from constants import COLOR_HP, COLOR_PP


def _load_frames(folder: str) -> list[pygame.Surface]:
    if not os.path.isdir(folder):
        return []
    files = sorted(
        (f for f in os.listdir(folder) if f.endswith(".png")),
        key=lambda f: int(os.path.splitext(f)[0])
        if os.path.splitext(f)[0].split(".")[0].isdigit()
        else f,
    )
    return [pygame.image.load(os.path.join(folder, f)).convert_alpha() for f in files]


def _tint_red(surface: pygame.Surface, alpha: int = 120) -> pygame.Surface:
    tinted = surface.copy()
    red = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
    red.fill((255, 0, 0, alpha))
    tinted.blit(red, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
    return tinted


class Brainrot:
    def __init__(
        self,
        name: str,
        max_hp: int,
        max_energy: int,
        lore_text: str,
        portrait_img: str,
        idle_anim: dict,
        skills: list,
    ):
        self.name, self.max_hp, self.hp = name, max_hp, max_hp
        self.max_energy, self.energy = max_energy, max_energy
        self.lore_text, self.portrait_img = lore_text, portrait_img
        self.skills = skills
        self.skip_turn_flag = False
        self.status_effects: list[StatusEffect] = []
        self.damage_multiplier = 1.0
        self.pp_multiplier = 1.0
        self.next_attack_mult = 1.0
        self.next_energy_mult = 1.0
        self.nullify_next_attack = False
        self.reflect_on_next_direct = (False, 0, 0)
        self.pending_effects: Dict[str, float | bool] = {}
        self.last_damage_taken = 0
        self.last_energy_lost = 0
        self._current_skill = None
        self.pos = (0, 0)
        self.flipped = False
        self._idle_path = idle_anim["file_root"]
        self._idle_fps = idle_anim.get("fps", 6)
        self._foot_offset = idle_anim.get("foot_offset", 0)
        self._frames_idle: list[pygame.Surface] = []
        self._frames_idle_red: list[pygame.Surface] = []
        self._state = "idle"
        self._frames_active = []
        self._fps_active = self._idle_fps
        self._frame_idx = 0
        self._time_acc = 0
        self._freeze_time = 0
        self._tint_time = 0
        self._move_fn = None
        self._orig_pos = None
        self._hit_start_frame = -1
        self._hit_end_frame = -1
        self._defender_ref = None
        self._red_active = False
        self._defended_this_turn = False

    def add_status(self, new_status: StatusEffect, game_state=None):
        if any(isinstance(s, type(new_status)) for s in self.status_effects):
            return
        new_status.apply_effect(self)
        self.status_effects.append(new_status)
        if game_state:
            msg = STATUS_MESSAGES.get(new_status.name, {}).get("applied")
            if msg:
                game_state.show_message(msg)

    def process_statuses(self, game_state=None):
        for status in self.status_effects[:]:
            if not status.cured:
                status.tick_effect(self)
                tick_msg = STATUS_MESSAGES.get(status.name, {}).get("tick")
                if game_state and tick_msg:
                    game_state.show_message(tick_msg)
            status.try_cure()
            if status.cured:
                cure_msg = STATUS_MESSAGES.get(status.name, {}).get("cured")
                if game_state and cure_msg:
                    game_state.show_message(cure_msg)
                self.status_effects.remove(status)

    def take_damage(self, amount: int):
        real = int(amount * self.damage_multiplier)
        self.last_damage_taken = real
        self.hp = max(0, self.hp - real)

    def heal(self, amount: int):
        prev = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - prev

    def consume_energy(self, amount: int):
        real_cost = int(amount * self.pp_multiplier)
        self.last_energy_lost = real_cost
        self.energy = max(0, self.energy - real_cost)

    def restore_energy(self, amount: int):
        prev = self.energy
        self.energy = min(self.max_energy, self.energy + amount)
        return self.energy - prev

    def apply_pending_effects(self, event_list: list[BattleEvent]) -> bool:
        skip = False
        if self.pending_effects.get("skip_turn"):
            event_list.append(BattleEvent("info", f"{self.name} perdió su turno.", None))
            skip = True
        dmg_mod = self.pending_effects.get("damage_mod")
        if dmg_mod is not None:
            self.next_attack_mult = dmg_mod
            event_list.append(BattleEvent("info", f"Daño del próximo ataque reducido.", COLOR_HP))
        pp_mod = self.pending_effects.get("energy_mod")
        if pp_mod is not None:
            self.next_energy_mult = pp_mod
            event_list.append(BattleEvent("info", f"Coste de PP del próximo ataque aumentado.", COLOR_PP))
        if self.pending_effects.get("nullify"):
            self.nullify_next_attack = True
        self.pending_effects.clear()
        return skip

    def is_dead(self) -> bool:
        return self.hp <= 0

    def reset(self):
        self.hp = self.max_hp
        self.energy = self.max_energy
        self.skip_turn_flag = False
        self.status_effects.clear()
        self.damage_multiplier = 1.0
        self.pp_multiplier = 1.0
        self.next_attack_mult = 1.0
        self.next_energy_mult = 1.0
        self.nullify_next_attack = False
        self.reflect_on_next_direct = (False, 0, 0)
        self.pending_effects.clear()
        self.last_damage_taken = 0
        self.last_energy_lost = 0
        self._red_active = False
        self._defended_this_turn = False
        self._set_idle()

    def load_assets(self):
        if not self._frames_idle:
            self._frames_idle = _load_frames(self._idle_path)
            self._frames_active = self._frames_idle or []
            self._frame_idx = 0
        if not self._frames_idle_red:
            char_folder = os.path.basename(os.path.dirname(self._idle_path))
            dmg_path = os.path.join("assets", "animations", "Damaged", f"{char_folder}_damaged", "idle")
            self._frames_idle_red = _load_frames(dmg_path)

    def start_skill_animation(self, skill, defender, sound_manager=None):
        self._current_skill = skill
        anim = skill.animation or {}
        self._frames_active = _load_frames(anim.get("file_root", "")) or self._frames_idle
        self._fps_active = anim.get("fps", 6)
        self._frame_idx = self._time_acc = 0
        self._state = "skill"
        self._freeze_frame = anim.get("freeze_frame", 0)
        if skill.is_defense and anim.get("freeze"):
            self._freeze_total = -1
        else:
            self._freeze_total = anim.get("freeze_time", 0) if anim.get("freeze") else 0
        self._move_fn = anim.get("movement_fn") if anim.get("movement") else None
        self._orig_pos = self.pos
        self._hit_start_frame = anim.get("hit_start", -1)
        self._hit_end_frame = anim.get("hit_end", self._hit_start_frame)
        self._defender_ref = defender if self._hit_start_frame >= 0 else None
        if skill.is_defense:
            self._defended_this_turn = True
        if sound_manager and anim.get("sound"):
            cb = anim.get("sound_fn")
            if cb:
                cb() if callable(cb) else sound_manager.play(cb)

    def resume_freeze(self):
        if self._state == "freeze" and self._freeze_total == -1:
            self._set_idle()

    def update(self, dt_ms: int):
        if not self._frames_idle:
            self.load_assets()
        if self._tint_time > 0:
            self._tint_time = max(0, self._tint_time - dt_ms)
        if self._state == "freeze":
            if self._freeze_total == -1:
                return
            self._freeze_time -= dt_ms
            if self._freeze_time <= 0:
                self._set_idle()
            return
        if not self._frames_active:
            return
        self._time_acc += dt_ms
        frame_time = 1000 / self._fps_active if self._fps_active else 1000
        while self._time_acc >= frame_time:
            self._time_acc -= frame_time
            self._frame_idx += 1
            if self._state == "skill":
                if self._defender_ref:
                    if self._frame_idx == self._hit_start_frame:
                        if not self._defender_ref._defended_this_turn:
                            self._defender_ref._red_active = True
                            self._defender_ref._frame_idx = 0
                    if self._frame_idx == self._hit_end_frame + 1:
                        self._defender_ref._red_active = False
                if self._freeze_total and self._freeze_total != -1 and self._frame_idx == self._freeze_frame:
                    self._state = "freeze"
                    self._freeze_time = self._freeze_total
                    return
                if self._freeze_total == -1 and self._frame_idx == self._freeze_frame:
                    self._state = "freeze"
                    return
            if self._frame_idx >= len(self._frames_active):
                self._set_idle()
                break
        if self._move_fn:
            self._move_fn(self, dt_ms)

    def draw(self, screen: pygame.Surface):
        if not self._frames_idle:
            self.load_assets()
        if not self._frames_active:
            return
        use_red = self._state == "idle" and self._red_active and self._frames_idle_red
        frames = self._frames_idle_red if use_red else self._frames_active
        frame = frames[self._frame_idx % len(frames)]
        if self.flipped:
            frame = pygame.transform.flip(frame, True, False)
        if self._tint_time > 0 and not use_red:
            frame = _tint_red(frame)
        fw, fh = frame.get_size()
        sw, sh = screen.get_size()
        cx = int((self.pos[0] / 33.867) * sw)
        cy = int((self.pos[1] / 19.05) * sh)
        screen.blit(frame, (cx - fw // 2, cy - fh))

    def _set_idle(self):
        self._state = "idle"
        self._frames_active = self._frames_idle
        self._fps_active = self._idle_fps
        self._frame_idx = self._time_acc = 0
        if self._move_fn and self._orig_pos:
            self.pos = self._orig_pos
        self._move_fn = self._orig_pos = None
        self._current_skill = None