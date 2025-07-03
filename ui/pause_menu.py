import pygame

OPTIONS = ["Reiniciar partida", "Volver al menú principal"]

FONT_PATH       = "assets/fonts/retro_gaming.ttf"
FONT_SIZE_TITLE = 80
FONT_SIZE_OPT   = 60

WHITE  = (255, 255, 255)
YELLOW = (255, 255,   0)
BLACK  = (0,   0,     0)

def run_pause_menu(screen: pygame.Surface, sound_manager, background: pygame.Surface | None = None):
    clock       = pygame.time.Clock()
    font_title  = pygame.font.Font(FONT_PATH, FONT_SIZE_TITLE)

    selected = 0
    overlay  = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))      # 50 % de opacidad

    while True:
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill((0, 0, 0))

        screen.blit(overlay, (0, 0))

        title_surf = font_title.render("PAUSA", True, WHITE)
        title_shad = font_title.render("PAUSA", True, BLACK)
        t_rect = title_surf.get_rect(center=(screen.get_width() // 2,
                                             screen.get_height() // 3))
        screen.blit(title_shad, (t_rect.x + 4, t_rect.y + 4))
        screen.blit(title_surf,  t_rect)

        rects = []
        for i, text in enumerate(OPTIONS):
            sel   = (i == selected)
            col   = YELLOW if sel else WHITE
            scale = 1.15  if sel else 1.0
            font  = pygame.font.Font(FONT_PATH, int(FONT_SIZE_OPT * scale))

            surf   = font.render(text, True, col)
            shadow = font.render(text, True, BLACK)
            y_pos  = screen.get_height() // 2 + i * (FONT_SIZE_OPT + 60)
            r      = surf.get_rect(center=(screen.get_width() // 2, y_pos))

            screen.blit(shadow, (r.x + 3, r.y + 3))
            screen.blit(surf,   r)
            rects.append(r)

        pygame.display.flip()

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return "QUIT"

            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(OPTIONS)
                    sound_manager.play("fx_select")
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(OPTIONS)
                    sound_manager.play("fx_select")
                elif ev.key == pygame.K_RETURN:
                    return OPTIONS[selected]
                elif ev.key == pygame.K_ESCAPE:
                    return None

            if ev.type == pygame.MOUSEMOTION:
                for i, r in enumerate(rects):
                    if r.collidepoint(ev.pos) and selected != i:
                        selected = i
                        sound_manager.play("fx_select")

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                for i, r in enumerate(rects):
                    if r.collidepoint(ev.pos):
                        return OPTIONS[i]

        clock.tick(60)