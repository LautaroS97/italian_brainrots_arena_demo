import os, random, pygame
from typing import List, Optional
from game.battle import BattleManager
from game.battle_event import BattleEvent
from game.scenarios import SCENARIOS
from ui.battle_ui import BattleUI
from utils import get_responsive_rect, REF_WIDTH_CM, REF_HEIGHT_CM
from game.brainrots.vaca_saturno_saturnita import get_brainrot as _vaca
from game.brainrots.lirili_larila import get_brainrot as _lirili
from game.brainrots.bombardino_crocodilo import get_brainrot as _bombardino
from game.brainrots.br_br_patapim import get_brainrot as _patapim
from game.brainrots.tralalero_tralala import get_brainrot as _tralalero
from game.brainrots.tung_tung_sahur import get_brainrot as _tung

MESSAGE_DELAY_MS = 2000
_WIN_LOSE_CH = 3
VICTORY_DONE_EVENT = pygame.USEREVENT + 1

end_menu_ready = False

player1 = player2 = battle = battle_ui = None
background_img = platform_img = interface_img = None
sound_manager = None
battle_has_ended = False
events_queue: List[BattleEvent] = []
current_event: Optional[BattleEvent] = None
animator = None
pause_timer = 0
_intro_pending = False
_intro_counter = 0

class TextAnimator:
    def __init__(self, full_text: str, speed: int = 25):
        self.full = full_text
        self.idx = 0
        self.spd = speed
        self.tmr = 0
    def update(self, dt: int):
        self.tmr += dt
        while self.tmr >= self.spd and self.idx < len(self.full):
            self.idx += 1
            self.tmr -= self.spd
    def is_finished(self) -> bool:
        return self.idx >= len(self.full)
    def text(self) -> str:
        return self.full[: self.idx]

_tmp = [(_vaca(), _vaca), (_lirili(), _lirili), (_bombardino(), _bombardino),
        (_patapim(), _patapim), (_tralalero(), _tralalero), (_tung(), _tung)]
_BRAINROT_FACTORIES = {i.name: fn for i, fn in _tmp}
del _tmp

def get_battle():
    return battle

def get_sound_manager():
    return sound_manager

def _play_skill_animation(event: BattleEvent):
    if " usó " not in event.text:
        return
    actor_name, skill_part = event.text.split(" usó ", 1)
    skill_name = skill_part.rstrip(".")
    actor = player1 if player1.name == actor_name else player2
    defender = player2 if actor is player1 else player1
    skill = next((s for s in actor.skills if s.name == skill_name), None)
    if skill:
        actor.start_skill_animation(skill, defender, sound_manager)

def init_battle(selected_data, sm=None, opponent_name=None, scenario_data=None):
    global player1, player2, battle, battle_ui, background_img, platform_img, interface_img
    global sound_manager, events_queue, current_event, animator, pause_timer
    global battle_has_ended, _intro_pending, _intro_counter, end_menu_ready
    name = selected_data["name"] if isinstance(selected_data, dict) else selected_data
    player1 = _BRAINROT_FACTORIES[name]()
    if opponent_name and opponent_name in _BRAINROT_FACTORIES:
        player2 = _BRAINROT_FACTORIES[opponent_name]()
    else:
        opp = random.choice([n for n in _BRAINROT_FACTORIES if n != player1.name])
        player2 = _BRAINROT_FACTORIES[opp]()
    player1.load_assets()
    player2.load_assets()
    w_px, h_px = player1._frames_idle[0].get_size()
    w_cm = w_px * (REF_WIDTH_CM / 1920)
    h_cm = h_px * (REF_HEIGHT_CM / 1080)
    player1.pos, player1.flipped = (7 + w_cm / 2, 2.86 + h_cm), False
    player2.pos, player2.flipped = (REF_WIDTH_CM - 7 - w_cm / 2, 2.86 + h_cm), True
    sound_manager = sm
    scr = pygame.display.get_surface()
    sw, sh = scr.get_size()
    scn = scenario_data if scenario_data else random.choice(SCENARIOS)
    background_img = pygame.transform.scale(pygame.image.load(scn["background"]).convert(), (sw, sh))
    platform_img = pygame.transform.scale(
        pygame.image.load(scn["platform"]).convert_alpha(),
        get_responsive_rect(0, 0, 10.92, 6, scr).size,
    )
    key = os.path.basename(scn["background"]).replace("_landscape.png", "")
    interface_img = pygame.transform.scale(
        pygame.image.load(f"assets/sprites/menu/{key}_menu.png").convert_alpha(),
        get_responsive_rect(0, 0, 33.85, 5.97, scr).size,
    )
    battle = BattleManager(player1, player2, sound_manager)
    battle.scenario = scn
    battle_ui = BattleUI(scr, player1, player2)
    events_queue = battle.get_events()
    current_event = None
    animator = None
    pause_timer = 0
    battle_has_ended = False
    end_menu_ready = False
    _intro_pending = True
    _intro_counter = 0
    pygame.mixer.set_num_channels(max(_WIN_LOSE_CH + 1, pygame.mixer.get_num_channels()))
    pygame.mixer.Channel(_WIN_LOSE_CH).set_endevent(VICTORY_DONE_EVENT)

def _enqueue_events():
    global events_queue, current_event, animator, pause_timer
    events_queue = battle.get_events()
    current_event = None
    animator = None
    pause_timer = 0

def _cpu_turn():
    if battle.get_active_player() != player2 or battle.is_game_over():
        return
    pygame.time.delay(400)
    battle.apply_action(random.choice(player2.skills))
    _enqueue_events()

def handle_battle_event(event):
    if event.type == pygame.KEYDOWN:
        idx_map = {pygame.K_a: 0, pygame.K_s: 1, pygame.K_d: 2, pygame.K_f: 3}
        if event.key in idx_map and battle.get_active_player() == player1:
            idx = idx_map[event.key]
            if idx < len(player1.skills):
                battle_ui.buttons_enabled = False
                battle.apply_action(player1.skills[idx])
                _enqueue_events()
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and battle_ui:
        if battle.get_active_player() == player1:
            skill = battle_ui.handle_click(event.pos)
            if skill:
                battle_ui.buttons_enabled = False
                battle.apply_action(skill)
                _enqueue_events()

def update_battle_logic(dt):
    global animator, current_event, pause_timer, _intro_pending, _intro_counter, battle_has_ended
    if battle:
        player1.update(dt)
        player2.update(dt)
    if _intro_pending:
        _intro_counter += 1
        if _intro_counter >= 2:
            _intro_pending = False
            if sound_manager:
                sound_manager.play_intro_sequence(player1.name, player2.name)
    if not current_event and events_queue:
        current_event = events_queue.pop(0)
        animator = TextAnimator(current_event.text)
        if current_event.kind == "skill":
            _play_skill_animation(current_event)
    if animator:
        animator.update(dt)
        if animator.is_finished():
            pause_timer += dt
            if pause_timer >= MESSAGE_DELAY_MS:
                pause_timer = 0
                current_event = None
                animator = None
                if not events_queue:
                    if battle.is_game_over():
                        _handle_end()
                    elif battle.get_active_player() == player1:
                        battle_ui.buttons_enabled = True
                    else:
                        _cpu_turn()

def _handle_end():
    global battle_has_ended
    if battle_has_ended or not battle or not battle.is_game_over():
        return
    battle_has_ended = True
    if sound_manager:
        sound_manager.stop("fx_combat_curtain")
        battle.play_victory_sound()
        snd = "fx_win" if battle.winner == player1.name else "fx_lose"
        pygame.mixer.Channel(_WIN_LOSE_CH).play(sound_manager._get(snd))

def draw_battle_placeholder(screen):
    screen.blit(background_img, (0, 0))
    screen.blit(platform_img, get_responsive_rect(6.15, 6.95, 0, 0, screen).topleft)
    screen.blit(platform_img, get_responsive_rect(16.79, 6.95, 0, 0, screen).topleft)
    front = None
    if player1._state == "skill" and not (player1._current_skill and player1._current_skill.render_behind_rival):
        front = player1
    elif player2._state == "skill" and not (player2._current_skill and player2._current_skill.render_behind_rival):
        front = player2
    if front is player1:
        player2.draw(screen)
        player1.draw(screen)
    elif front is player2:
        player1.draw(screen)
        player2.draw(screen)
    else:
        player1.draw(screen)
        player2.draw(screen)
    screen.blit(interface_img, get_responsive_rect(0.02, 13.05, 0, 0, screen).topleft)
    if battle_ui:
        battle_ui.draw(animator, current_event)