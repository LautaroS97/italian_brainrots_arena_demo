import pygame
import os
import unicodedata
import re

class SoundManager:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.sounds = {}
        self.loop_channels = {}
        self.channels = {
            "effects": pygame.mixer.Channel(0),
            "voices": pygame.mixer.Channel(1),
            "ambient": pygame.mixer.Channel(2),
        }
        pygame.mixer.init()

    # ---------- Normalización de nombres ----------
    @staticmethod
    def _normalize(name: str) -> str:
        name = unicodedata.normalize("NFKD", name)
        name = name.encode("ascii", "ignore").decode("ascii").lower()
        name = re.sub(r"\s+", "_", name)
        name = re.sub(r"[^a-z0-9_]", "", name)
        return name

    # ---------- Carga ----------
    def load_sound(self, key: str, relative_path: str):
        key_norm = self._normalize(key)
        abs_path = os.path.join(self.base_path, relative_path)
        if os.path.isfile(abs_path):
            self.sounds[key_norm] = pygame.mixer.Sound(abs_path)
        else:
            print(f"[SoundManager] Archivo no encontrado: {abs_path}")

    def load_all(self, brainrot_names: list[str]):
        for name in brainrot_names:
            self.load_sound(f"fx_{name}", f"brainrots/fx_{self._normalize(name)}.mp3")

        common = {
            "fx_versus": "combat/fx_versus.mp3",
            "fx_start_fight": "combat/fx_start_fight.mp3",
            "fx_end_energy": "combat/fx_end_energy.mp3",
            "fx_end_health": "combat/fx_end_health.mp3",
            "fx_winner_for_energy": "combat/fx_winner_for_energy.mp3",
            "fx_winner_for_health": "combat/fx_winner_for_health.mp3",
            "fx_menu_curtain": "menu/fx_menu_curtain.mp3",
            "fx_combat_curtain": "menu/fx_combat_curtain.mp3",
            "fx_win": "menu/fx_win.mp3",
            "fx_lose": "menu/fx_lose.mp3",
            "fx_select": "menu/fx_select.mp3",
            "fx_congratulation": "menu/fx_congratulation.mp3",
            "fx_back": "menu/fx_back.mp3",
            "fx_error": "menu/fx_error.mp3",
        }
        for key, path in common.items():
            self.load_sound(key, path)

    # ---------- Reproducción ----------
    def _get(self, key: str):
        return self.sounds.get(self._normalize(key))

    def play(self, key: str, volume: float = 1.0, channel: str = "effects"):
        snd = self._get(key)
        if snd:
            ch = self.channels.get(channel)
            if ch:
                snd.set_volume(volume)
                ch.play(snd)
            else:
                snd.set_volume(volume)
                snd.play()
        else:
            print(f"[SoundManager] Sound '{key}' not found.")

    def play_loop(self, key: str, volume: float = 1.0):
        snd = self._get(key)
        if snd:
            ch = self.channels["ambient"]
            snd.set_volume(volume)
            ch.play(snd, loops=-1)
            self.loop_channels[key] = ch
        else:
            print(f"[SoundManager] Sound '{key}' not found.")

    def ensure_loop(self, key: str, volume: float = 1.0):
        snd = self._get(key)
        ch = self.channels["ambient"]
        if snd and not ch.get_busy():
            snd.set_volume(volume)
            ch.play(snd, loops=-1)
            self.loop_channels[key] = ch

    def stop(self, key: str):
        ch = self.loop_channels.get(key)
        if ch:
            ch.stop()
            self.loop_channels.pop(key, None)

    def stop_all_loops(self):
        for ch in self.loop_channels.values():
            if ch:
                ch.stop()
        self.loop_channels.clear()

    def stop_all_channels(self):
        for ch in self.channels.values():
            ch.stop()

    # ---------- Secuencias prefabricadas ----------
    def play_intro_sequence(self, name1: str, name2: str):
        self.play(f"fx_{name1}", volume=1.5, channel="voices")
        while self.channels["voices"].get_busy():
            pygame.time.wait(100)
        self.play("fx_versus", volume=1.0, channel="voices")
        while self.channels["voices"].get_busy():
            pygame.time.wait(100)
        self.play(f"fx_{name2}", volume=1.5, channel="voices")
        while self.channels["voices"].get_busy():
            pygame.time.wait(100)
        self.play("fx_start_fight", volume=1.0, channel="voices")

    def play_victory_energy(self, loser: str, winner: str):
        self.play(f"fx_{loser}", volume=1.5, channel="voices")
        while self.channels["voices"].get_busy():
            pygame.time.wait(100)
        self.play("fx_end_energy", volume=1.0, channel="effects")
        while self.channels["effects"].get_busy():
            pygame.time.wait(100)
        self.play(f"fx_{winner}", volume=1.5, channel="voices")
        while self.channels["voices"].get_busy():
            pygame.time.wait(100)
        self.play("fx_winner_for_energy", volume=1.0, channel="effects")
        while self.channels["effects"].get_busy():
            pygame.time.wait(100)

    def play_victory_health(self, loser: str, winner: str):
        self.play(f"fx_{loser}", volume=1.5, channel="voices")
        while self.channels["voices"].get_busy():
            pygame.time.wait(100)
        self.play("fx_end_health", volume=1.0, channel="effects")
        while self.channels["effects"].get_busy():
            pygame.time.wait(100)
        self.play(f"fx_{winner}", volume=1.5, channel="voices")
        while self.channels["voices"].get_busy():
            pygame.time.wait(100)
        self.play("fx_winner_for_health", volume=1.0, channel="effects")
        while self.channels["effects"].get_busy():
            pygame.time.wait(100)