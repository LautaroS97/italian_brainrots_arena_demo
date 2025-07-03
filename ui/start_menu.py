import pygame

OPTIONS = ["Jugar", "Salir"]
FONT_PATH = "assets/fonts/retro_gaming.ttf"
FONT_SIZE = 60
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)

def run_start_menu(screen, sound_manager, background=None):
    clock = pygame.time.Clock()
    base_font = pygame.font.Font(FONT_PATH, FONT_SIZE)
    selected_index = 0
    running = True
    animating_selection = True
    option_rects = []

    # Superficie negra semitransparente (50%)
    dark_overlay = pygame.Surface(screen.get_size()).convert_alpha()
    dark_overlay.fill((0, 0, 0, 128))  # 128 = 50% opacidad

    # Cargar gráfico de personajes del menú
    menu_characters = pygame.image.load("assets/sprites/props/menu_characters.png").convert_alpha()
    menu_characters = pygame.transform.scale(menu_characters, (550, 300))
    menu_characters_rect = menu_characters.get_rect(midtop=(screen.get_width() // 2, int(screen.get_height() * 0.15)))

    while running:
        # Fondo
        if background:
            screen.blit(background, (0, 0))

        # Capa negra semitransparente
        screen.blit(dark_overlay, (0, 0))

        # Personajes del menú por delante de la oscuridad
        screen.blit(menu_characters, menu_characters_rect)

        option_rects.clear()

        for i, option in enumerate(OPTIONS):
            is_selected = (i == selected_index)
            color = YELLOW if is_selected and animating_selection else WHITE

            # Ajustar tamaño de fuente según selección
            size_multiplier = 1.25 if is_selected and animating_selection else 1
            font = pygame.font.Font(FONT_PATH, int(FONT_SIZE * size_multiplier))

            text_surface = font.render(option, True, color)
            shadow_surface = font.render(option, True, BLACK)

            x = screen.get_width() // 2
            y = screen.get_height() // 2 + i * (FONT_SIZE + 60)
            text_rect = text_surface.get_rect(center=(x, y))
            shadow_rect = shadow_surface.get_rect(center=(x + 3, y + 3))

            screen.blit(shadow_surface, shadow_rect)
            screen.blit(text_surface, text_rect)
            option_rects.append(text_rect)

        pygame.display.flip()

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
                    animating_selection = False
                    pygame.display.flip()
                    pygame.time.delay(200)
                    return handle_selection(selected_index, sound_manager)

            elif event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(event.pos) and selected_index != i:
                        selected_index = i
                        sound_manager.play("fx_select")

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(event.pos):
                        selected_index = i
                        animating_selection = False
                        pygame.display.flip()
                        pygame.time.delay(200)
                        return handle_selection(selected_index, sound_manager)

        clock.tick(60)

def handle_selection(index, sound_manager):
    if OPTIONS[index] == "Jugar":
        sound_manager.play("fx_congratulation")
        return "CHARACTER_SELECT"
    elif OPTIONS[index] == "Salir":
        sound_manager.play("fx_error")
        return "QUIT"