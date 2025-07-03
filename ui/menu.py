import os
import pygame
from game.brainrot import _load_frames           # reutilizamos el loader
from game.brainrots_registry import BRAINROTS    # lista de objetos Brainrot
from utils import get_responsive_rect

pygame.font.init()

# ───────── Fuentes ─────────
title_font  = pygame.font.Font("assets/fonts/retro_gaming.ttf", 72)
button_font = pygame.font.Font("assets/fonts/retro_gaming.ttf", 42)
back_font   = pygame.font.Font("assets/fonts/retro_gaming.ttf", 30)
name_font   = pygame.font.Font("assets/fonts/upheavtt.ttf",     22)

# ───────── Estado global del selector ─────────
selected_index     = 0
last_index         = -1
character_thumbs   = []   # [(rect, brainrot_obj)]
back_button_rect   = None
back_button_hover  = False
idle_animations    = {}   # {brainrot: {"frames": [...], "idx": 0, "last_time": ms}}

# ───────── Parámetros visuales ─────────
THUMB_W_CM, THUMB_H_CM = 5.3, 5.3
GRID_COLS              = 3
GRID_SPACING_X_CM      = 2.5
GRID_SPACING_Y_CM      = 2.4
GRID_TOP_CM            = 5.3

# ──────────────────────────────────────────────────────────────
# Dibujar Selector de Personajes
# ──────────────────────────────────────────────────────────────
def draw_character_select(screen, sound_manager=None, background_img=None):
    global character_thumbs, back_button_rect, back_button_hover
    screen_w, _ = screen.get_size()

    # Fondo
    if background_img:
        screen.blit(pygame.transform.scale(background_img, screen.get_size()), (0, 0))
    else:
        screen.fill((30, 30, 30))

    # Título
    x, y = get_responsive_rect(0, 1.5, 0, 0, screen).topleft
    title_shadow = title_font.render("ELIGE TU PERSONAJE", True, (0, 0, 0))
    title_text   = title_font.render("ELIGE TU PERSONAJE", True, (255, 255, 255))
    screen.blit(title_shadow, title_shadow.get_rect(midtop=(screen_w // 2 + 2, y + 2)))
    screen.blit(title_text,   title_text.get_rect(midtop=(screen_w // 2,     y)))

    # Botón Volver
    back_color   = (255, 255, 0) if back_button_hover else (255, 255, 255)
    back_shadow  = back_font.render("Volver al menú principal", True, (0, 0, 0))
    back_text    = back_font.render("Volver al menú principal", True, back_color)
    back_button_rect = back_text.get_rect(topleft=(40, 30))
    screen.blit(back_shadow, back_button_rect.move(2, 2))
    screen.blit(back_text,   back_button_rect)

    # Layout Thumbnails
    thumb_w   = get_responsive_rect(0, 0, THUMB_W_CM, THUMB_H_CM, screen).width
    thumb_h   = get_responsive_rect(0, 0, THUMB_W_CM, THUMB_H_CM, screen).height
    spacing_x = get_responsive_rect(0, 0, GRID_SPACING_X_CM, 0, screen).width
    spacing_y = get_responsive_rect(0, 0, 0, GRID_SPACING_Y_CM, screen).height
    grid_top_y = get_responsive_rect(0, GRID_TOP_CM, 0, 0, screen).y
    total_width = GRID_COLS * thumb_w + (GRID_COLS - 1) * spacing_x
    start_x = (screen_w - total_width) // 2

    # ── Animar frames idle ──
    now_ms = pygame.time.get_ticks()
    for char in BRAINROTS:
        if char not in idle_animations:
            frames = _load_frames(char._idle_path) or [pygame.Surface((thumb_w, thumb_h), pygame.SRCALPHA)]
            idle_animations[char] = {"frames": frames, "idx": 0, "last": now_ms}
        else:
            anim = idle_animations[char]
            if now_ms - anim["last"] > 1000 // char._idle_fps:
                anim["idx"]  = (anim["idx"] + 1) % len(anim["frames"])
                anim["last"] = now_ms

    # ── Render thumbnails ──
    character_thumbs.clear()
    mouse_pos = pygame.mouse.get_pos()

    for i, char in enumerate(BRAINROTS):
        col, row = i % GRID_COLS, i // GRID_COLS
        x = start_x + col * (thumb_w + spacing_x)
        y = grid_top_y + row * (thumb_h + spacing_y)

        selected = (i == selected_index)
        scale    = 1.25 if selected else 1
        tw, th   = int(thumb_w * scale), int(thumb_h * scale)
        offset_x, offset_y = (tw - thumb_w)//2, (th - thumb_h)//2

        # Frame actual del idle
        full_frame = idle_animations[char]["frames"][idle_animations[char]["idx"]]
        frame_w, frame_h = full_frame.get_size()
        cropped_frame = full_frame.subsurface(pygame.Rect(0, 0, frame_w // 2, frame_h))
        img = pygame.transform.scale(cropped_frame, (tw, th))
        rect = pygame.Rect(x - offset_x, y - offset_y, tw, th)

        screen.blit(img, rect.topleft)
        pygame.draw.rect(screen, (255, 255, 0) if selected else (255, 255, 255), rect, 4)

        # Nombre
        name_s  = name_font.render(char.name.upper(), True, (255, 255, 255))
        shadow  = name_font.render(char.name.upper(), True, (0, 0, 0))
        name_r  = name_s.get_rect(center=(x + thumb_w // 2, y + thumb_h + 28))
        screen.blit(shadow, name_r.move(2, 2))
        screen.blit(name_s,  name_r)

        character_thumbs.append((rect, char))

# ──────────────────────────────────────────────────────────────
# Manejo de eventos
# ──────────────────────────────────────────────────────────────
def handle_character_select_event(event, sound_manager=None):
    global selected_index, last_index, back_button_hover

    if event.type == pygame.MOUSEMOTION:
        back_button_hover = back_button_rect.collidepoint(event.pos) if back_button_rect else False
        for i, (rect, _) in enumerate(character_thumbs):
            if rect.collidepoint(event.pos) and i != selected_index:
                selected_index = i
                if sound_manager: sound_manager.play("fx_select")

    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        # Clic en volver
        if back_button_rect and back_button_rect.collidepoint(event.pos):
            if sound_manager: sound_manager.play("fx_error")
            pygame.display.flip(); pygame.time.delay(200)
            return "back"

        # Clic en un personaje
        for i, (rect, char) in enumerate(character_thumbs):
            if rect.collidepoint(event.pos):
                selected_index = i
                if sound_manager: sound_manager.play("fx_congratulation")
                pygame.display.flip(); pygame.time.delay(200)
                return {"name": char.name}

    elif event.type == pygame.KEYDOWN:
        total = len(BRAINROTS)
        move  = 0
        if event.key in (pygame.K_LEFT,  pygame.K_a): move = -1
        if event.key in (pygame.K_RIGHT, pygame.K_d): move = +1
        if event.key in (pygame.K_UP,    pygame.K_w): move = -GRID_COLS
        if event.key in (pygame.K_DOWN,  pygame.K_s): move = +GRID_COLS

        if move:
            new_i = selected_index + move
            if 0 <= new_i < total:
                selected_index = new_i
                if sound_manager and new_i != last_index:
                    sound_manager.play("fx_select")
                last_index = new_i
            return None

        if event.key == pygame.K_RETURN:
            if sound_manager: sound_manager.play("fx_congratulation")
            pygame.display.flip(); pygame.time.delay(200)
            return {"name": BRAINROTS[selected_index].name}

        if event.key == pygame.K_ESCAPE:
            if sound_manager: sound_manager.play("fx_error")
            pygame.display.flip(); pygame.time.delay(200)
            return "back"

    return None