import pygame, sys
from ui import menu, start_menu, end_menu, pause_menu
import game.game_state as gs
from game.game_state import (
    init_battle, draw_battle_placeholder, handle_battle_event,
    update_battle_logic, VICTORY_DONE_EVENT,
)
from game.sound_manager import SoundManager
from utils import get_responsive_rect

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption("Italian Brainrots Arena")
clock, FPS = pygame.time.Clock(), 60

FRONT, START_MENU, CHARACTER_SELECT, BATTLE, PAUSE_MENU, END_MENU = (
    "front", "start_menu", "character_select", "battle", "pause_menu", "end_menu"
)
current_state = FRONT

selected_character = winner_name = None
battle_snapshot = pause_snapshot = None

front_background = pygame.transform.scale(
    pygame.image.load("assets/sprites/backgrounds/front_landscape.png").convert(),
    (1920, 1080)
)
front_characters = pygame.transform.scale(
    pygame.image.load("assets/sprites/props/front_characters.png").convert_alpha(),
    get_responsive_rect(2.96, 1.67, 27.94, 15.72, screen).size
)
front_characters_rect = get_responsive_rect(2.96, 1.67, 27.94, 15.72, screen)
font_prompt = pygame.font.Font("assets/fonts/upheavtt.ttf", 36)

sound_manager = SoundManager("assets/sounds")
sound_manager.load_all([
    "tralalero_tralala", "bombardino_crocodilo", "br_br_patapim",
    "lirili_larila", "tung_tung_sahur", "vaca_saturno_saturnita",
    "fx_select", "fx_congratulation", "fx_error", "fx_back",
    "fx_menu_curtain", "fx_combat_curtain"
])

blink_timer = 0
show_text = True
BLINK_INTERVAL = 500

def draw_front_screen():
    screen.blit(front_background, (0, 0))
    screen.blit(front_characters, front_characters_rect.topleft)
    if show_text:
        txt = "Presione cualquier tecla o clic para comenzar"
        lbl = font_prompt.render(txt, True, (255, 255, 255))
        shd = font_prompt.render(txt, True, (0, 0, 0))
        r = lbl.get_rect(center=(screen.get_width() // 2, int(screen.get_height() * 0.85)))
        screen.blit(shd, (r.x + 2, r.y + 2))
        screen.blit(lbl, r)

def main():
    global current_state, selected_character, winner_name
    global battle_snapshot, pause_snapshot, blink_timer, show_text

    sound_manager.ensure_loop("fx_menu_curtain")
    running = True
    while running:
        dt = clock.tick(FPS)
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == VICTORY_DONE_EVENT:
                gs.end_menu_ready = True
                continue
            if event.type == pygame.QUIT:
                running = False

            if current_state == FRONT:
                if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    current_state = START_MENU

            elif current_state == CHARACTER_SELECT:
                res = menu.handle_character_select_event(event, sound_manager)
                if res == "back":
                    sound_manager.play("fx_back")
                    sound_manager.ensure_loop("fx_menu_curtain")
                    current_state = START_MENU
                elif res:
                    sound_manager.stop("fx_menu_curtain")
                    sound_manager.play("fx_congratulation")
                    selected_character = res
                    init_battle(selected_character, sound_manager)
                    sound_manager.play_loop("fx_combat_curtain", volume=0.1)
                    current_state = BATTLE

            elif current_state == BATTLE:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    current_state = PAUSE_MENU             
                else:
                    handle_battle_event(event)

        if current_state == FRONT:
            draw_front_screen()
            sound_manager.ensure_loop("fx_menu_curtain")

        elif current_state == START_MENU:
            sound_manager.ensure_loop("fx_menu_curtain")
            choice = start_menu.run_start_menu(screen, sound_manager, front_background)
            if choice == "CHARACTER_SELECT":
                current_state = CHARACTER_SELECT
            elif choice == "QUIT":
                pygame.quit(); sys.exit()

        elif current_state == CHARACTER_SELECT:
            sound_manager.ensure_loop("fx_menu_curtain")
            menu.draw_character_select(screen, sound_manager, front_background)

        elif current_state == BATTLE:
            draw_battle_placeholder(screen)
            update_battle_logic(dt)
            
            pause_snapshot = screen.copy()  

            if gs.battle and gs.battle.is_game_over() and gs.end_menu_ready:
                winner_name = gs.battle.winner
                battle_snapshot = screen.copy()
                current_state = END_MENU

        elif current_state == PAUSE_MENU:
            res = pause_menu.run_pause_menu(screen, sound_manager, background=pause_snapshot)
            if res == "Reiniciar partida":
                rival = gs.battle.player2.name if gs.battle else None
                scena = gs.battle.scenario if gs.battle else None
                sound_manager.stop("fx_menu_curtain")
                init_battle(selected_character, sound_manager,
                            opponent_name=rival, scenario_data=scena)
                sound_manager.play_loop("fx_combat_curtain", volume=0.1)
                current_state = BATTLE
            elif res == "Volver al menú principal":
                sound_manager.stop("fx_combat_curtain")
                sound_manager.ensure_loop("fx_menu_curtain")
                current_state = START_MENU
            elif res == "QUIT":
                pygame.quit(); sys.exit()
            else:
                sound_manager.stop("fx_menu_curtain")
                sound_manager.play_loop("fx_combat_curtain", volume=0.1)
                current_state = BATTLE

        elif current_state == END_MENU:
            res = end_menu.run_end_menu(
                screen, sound_manager, winner_name,
                background=battle_snapshot, player_name=selected_character["name"]
            )
            if res == "REPLAY":
                init_battle(selected_character, sound_manager)
                sound_manager.play_loop("fx_combat_curtain", volume=0.1)
                current_state = BATTLE
            elif res == "MAIN_MENU":
                sound_manager.ensure_loop("fx_menu_curtain")
                current_state = START_MENU
            elif res == "QUIT":
                pygame.quit(); sys.exit()

        if current_state == FRONT:
            blink_timer += dt
            if blink_timer >= BLINK_INTERVAL:
                show_text = not show_text
                blink_timer = 0

        pygame.display.flip()

    pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()