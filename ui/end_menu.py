import pygame

OPTIONS = ["Jugar de nuevo", "Volver al menú principal"]

# --- Estilos ---
FONT_PATH = "assets/fonts/retro_gaming.ttf"
FONT_SIZE_TITLE   = 80
FONT_SIZE_OPTIONS = 60

WHITE  = (255, 255, 255)
YELLOW = (255, 255,   0)
BLACK  = (  0,   0,   0)
RED    = (255,  60,  60)
GREEN  = ( 60, 255,  60)

def run_end_menu(screen: pygame.Surface,
                 sound_manager,
                 winner_name: str,
                 background: pygame.Surface | None = None,
                 player_name: str | None = None):
    """
    Muestra el menú final.
    - `winner_name`  : nombre del ganador.
    - `player_name`* : nombre de tu personaje (opcional, pero recomendable).
    - `background`   : Surface con la escena final; si None, dibuja negro.
    Devuelve "REPLAY", "MAIN_MENU" o "QUIT".
    """

    clock = pygame.time.Clock()
    font_title = pygame.font.Font(FONT_PATH, FONT_SIZE_TITLE)
    base_font  = pygame.font.Font(FONT_PATH, FONT_SIZE_OPTIONS)

    # --- Estado del menú ---
    selected_index = 0
    running        = True
    option_rects   = []

    # ¿Ganaste?
    you_won = (winner_name == player_name) if player_name else (winner_name.lower() == "player")
    title_text  = "GANASTE" if you_won else "PERDISTE"
    title_color = GREEN if you_won else RED

    # --- Overlay negro al 50 % ---
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))   # 128/255 ≈ 50 %

    while running:
        # --- Fondo congelado de la batalla ---
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill((0, 0, 0))      # fallback

        screen.blit(overlay, (0, 0))     # oscurecer

        # --- Título ---
        title_surface = font_title.render(title_text, True, title_color)
        title_shadow  = font_title.render(title_text, True, BLACK)
        title_rect    = title_surface.get_rect(center=(screen.get_width()//2,
                                                       screen.get_height()//3))
        screen.blit(title_shadow, (title_rect.x+4, title_rect.y+4))
        screen.blit(title_surface, title_rect)

        # --- Opciones ---
        option_rects.clear()
        for i, option in enumerate(OPTIONS):
            selected    = (i == selected_index)
            color       = YELLOW if selected else WHITE
            scale       = 1.15 if selected else 1.0
            font        = pygame.font.Font(FONT_PATH,
                                           int(FONT_SIZE_OPTIONS * scale))

            text_surf   = font.render(option, True, color)
            shadow_surf = font.render(option, True, BLACK)

            x = screen.get_width() // 2
            y = screen.get_height() // 2 + i * (FONT_SIZE_OPTIONS + 60)
            rect = text_surf.get_rect(center=(x, y))

            screen.blit(shadow_surf, (rect.x+3, rect.y+3))
            screen.blit(text_surf,   rect)
            option_rects.append(rect)

        pygame.display.flip()

        # --- Eventos ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected_index = (selected_index + 1) % len(OPTIONS)
                    sound_manager.play("fx_select")
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected_index = (selected_index - 1) % len(OPTIONS)
                    sound_manager.play("fx_select")
                elif event.key == pygame.K_RETURN:
                    return _handle_selection(selected_index, sound_manager)
                elif event.key == pygame.K_ESCAPE:
                    sound_manager.play("fx_back")
                    return "MAIN_MENU"

            elif event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(event.pos) and selected_index != i:
                        selected_index = i
                        sound_manager.play("fx_select")

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(event.pos):
                        selected_index = i
                        return _handle_selection(selected_index, sound_manager)

        clock.tick(60)

# -----------------------------------------------------------
def _handle_selection(index: int, sound_manager):
    if OPTIONS[index] == "Jugar de nuevo":
        sound_manager.play("fx_congratulation")
        return "REPLAY"
    else:                             
        sound_manager.play("fx_back")
        return "MAIN_MENU"
