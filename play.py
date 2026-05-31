"""
Snake — Retro Arcade Edition
Run:  python play.py
Keys: Arrow keys — move
      P          — pause / resume
      R          — restart
      Q / Esc    — quit
"""

import math
import sys
import pygame
from game.snake import SnakeGame, CELL, COLS, ROWS, WIDTH, HEIGHT

# ── Colours ────────────────────────────────────────────────────────────────────
BG          = (  5, 10, 14)
GRID_LINE   = ( 12, 28, 18)
HEAD_GREEN  = (  0,255, 85)
BODY_BASE   = (  0,200, 55)
FOOD_RED    = (255, 51, 85)
FOOD_SHINE  = (255,160,175)
HUD_ACCENT  = (  0,220, 70)
HUD_DIM     = ( 58,140, 90)
OVERLAY_BG  = (  5, 10, 14, 210)
PAUSE_TEXT  = (  0,180, 55)
OVER_RED    = (255, 48, 68)
WHITE       = (255,255,255)
BORDER      = ( 30, 80, 50)

# ── Window layout ──────────────────────────────────────────────────────────────
HUD_H    = 80
CTRL_H   = 30
WIN_W    = WIDTH
WIN_H    = HUD_H + HEIGHT + CTRL_H

pygame.init()
screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("SNAKE")
clock  = pygame.time.Clock()

# Fonts — fall back gracefully if the system doesn't have the preferred face
def load_font(size, bold=False):
    for name in ("Orbitron", "Consolas", "Courier New", "monospace"):
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            return f
        except Exception:
            pass
    return pygame.font.Font(None, size)

font_title  = load_font(32, bold=True)
font_hud    = load_font(22, bold=True)
font_label  = load_font(11)
font_ctrl   = load_font(13)
font_over   = load_font(38, bold=True)
font_hint   = load_font(14)

game    = SnakeGame()
paused  = False
started = False          # show "press any arrow key" screen first
tick_acc = 0             # ms accumulator for independent tick rate
frame   = 0              # used for food pulse animation


def reset():
    global paused, tick_acc
    game.reset()
    paused   = False
    tick_acc = 0


# ── Drawing helpers ─────────────────────────────────────────────────────────────

def draw_grid(surface, ox, oy):
    for c in range(COLS + 1):
        x = ox + c * CELL
        pygame.draw.line(surface, GRID_LINE, (x, oy), (x, oy + HEIGHT))
    for r in range(ROWS + 1):
        y = oy + r * CELL
        pygame.draw.line(surface, GRID_LINE, (ox, y), (ox + WIDTH, y))


def draw_snake(surface, ox, oy):
    n = len(game.snake)
    for i, (gx, gy) in enumerate(game.snake):
        x = ox + gx * CELL + 1
        y = oy + gy * CELL + 1
        sz = CELL - 2
        is_head = (i == 0)
        t = i / max(n - 1, 1)
        g = int(200 - t * 80)
        color = HEAD_GREEN if is_head else (0, g, 40)
        radius = 5 if is_head else 3
        rect = pygame.Rect(x, y, sz, sz)
        pygame.draw.rect(surface, color, rect, border_radius=radius)

        if is_head:
            # draw eyes relative to direction
            dx, dy = game.direction
            eye_color = BG
            eye_sz = 3
            if dx == 1:
                eyes = [(x + sz - 6, y + 4), (x + sz - 6, y + sz - 7)]
            elif dx == -1:
                eyes = [(x + 3, y + 4), (x + 3, y + sz - 7)]
            elif dy == -1:
                eyes = [(x + 4, y + 3), (x + sz - 7, y + 3)]
            else:
                eyes = [(x + 4, y + sz - 6), (x + sz - 7, y + sz - 6)]
            for ex, ey in eyes:
                pygame.draw.rect(surface, eye_color, (ex, ey, eye_sz, eye_sz))


def draw_food(surface, ox, oy):
    gx, gy = game.food
    cx = ox + gx * CELL + CELL // 2
    cy = oy + gy * CELL + CELL // 2
    pulse = 0.85 + 0.15 * math.sin(frame * 0.12)
    r = int(6 * pulse)
    pygame.draw.circle(surface, FOOD_RED, (cx, cy), r)
    pygame.draw.circle(surface, FOOD_SHINE, (cx - 2, cy - 2), max(1, r // 3))


def draw_hud(surface):
    # background bar
    pygame.draw.rect(surface, (8, 18, 12), (0, 0, WIN_W, HUD_H))
    pygame.draw.line(surface, BORDER, (0, HUD_H - 1), (WIN_W, HUD_H - 1))

    stats = [
        ("SCORE",  f"{game.score:02d}"),
        ("BEST",   f"{game.best:02d}"),
        ("LENGTH", f"{len(game.snake):02d}"),
    ]
    section_w = WIN_W // len(stats)
    for i, (label, val) in enumerate(stats):
        cx = section_w * i + section_w // 2
        lbl_surf = font_label.render(label, True, HUD_DIM)
        val_surf = font_hud.render(val, True, HUD_ACCENT)
        surface.blit(lbl_surf, lbl_surf.get_rect(centerx=cx, centery=28))
        surface.blit(val_surf, val_surf.get_rect(centerx=cx, centery=56))
        if i < len(stats) - 1:
            pygame.draw.line(surface, BORDER,
                             (section_w * (i + 1), 16),
                             (section_w * (i + 1), HUD_H - 16))


def draw_controls(surface, oy):
    pygame.draw.rect(surface, (6, 14, 10), (0, oy, WIN_W, CTRL_H))
    pygame.draw.line(surface, BORDER, (0, oy), (WIN_W, oy))
    hints = "↑↓←→  Move     P  Pause     R  Restart     Q  Quit"
    surf = font_ctrl.render(hints, True, HUD_DIM)
    surface.blit(surf, surf.get_rect(center=(WIN_W // 2, oy + CTRL_H // 2)))


def draw_overlay_text(surface, canvas_oy):
    """Semi-transparent overlay for game-over and start screens."""
    ovl = pygame.Surface((WIN_W, HEIGHT), pygame.SRCALPHA)
    ovl.fill(OVERLAY_BG)
    surface.blit(ovl, (0, canvas_oy))


def draw_game_over(surface, canvas_oy):
    draw_overlay_text(surface, canvas_oy)
    cy = canvas_oy + HEIGHT // 2
    over  = font_over.render("GAME OVER", True, OVER_RED)
    sub   = font_hint.render(
        f"SCORE: {game.score:02d}   BEST: {game.best:02d}", True, HUD_DIM)
    hint  = font_hint.render("R — Play Again    Q — Quit", True, HUD_ACCENT)
    surface.blit(over, over.get_rect(centerx=WIN_W // 2, centery=cy - 38))
    surface.blit(sub,  sub.get_rect(centerx=WIN_W // 2,  centery=cy + 4))
    surface.blit(hint, hint.get_rect(centerx=WIN_W // 2,  centery=cy + 30))


def draw_start_screen(surface, canvas_oy):
    draw_overlay_text(surface, canvas_oy)
    cy = canvas_oy + HEIGHT // 2
    title = font_hud.render("PRESS ANY ARROW KEY TO START", True, HUD_ACCENT)
    surface.blit(title, title.get_rect(centerx=WIN_W // 2, centery=cy))


def draw_pause(surface, canvas_oy):
    ovl = pygame.Surface((WIN_W, HEIGHT), pygame.SRCALPHA)
    ovl.fill((5, 10, 14, 160))
    surface.blit(ovl, (0, canvas_oy))
    cy = canvas_oy + HEIGHT // 2
    p    = font_over.render("PAUSED", True, PAUSE_TEXT)
    hint = font_hint.render("P — Resume", True, HUD_DIM)
    surface.blit(p,    p.get_rect(centerx=WIN_W // 2, centery=cy - 20))
    surface.blit(hint, hint.get_rect(centerx=WIN_W // 2, centery=cy + 18))


# ── Main loop ──────────────────────────────────────────────────────────────────

CANVAS_OY  = HUD_H
CTRL_OY    = HUD_H + HEIGHT
DIR_KEYS = {
    pygame.K_UP:    (0, -1),
    pygame.K_DOWN:  (0,  1),
    pygame.K_LEFT:  (-1, 0),
    pygame.K_RIGHT: ( 1, 0),
}

running = True
prev_ms = pygame.time.get_ticks()

while running:
    now_ms = pygame.time.get_ticks()
    dt     = now_ms - prev_ms
    prev_ms = now_ms
    frame  += 1

    # ── Events ────────────────────────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            key = event.key

            if key in (pygame.K_q, pygame.K_ESCAPE):
                running = False

            elif key == pygame.K_r:
                reset()
                started = True

            elif key == pygame.K_p and started and not game.done:
                paused = not paused

            elif key in DIR_KEYS:
                if not started:
                    started = True
                if not game.done:
                    game.change_direction(DIR_KEYS[key])

    # ── Game tick ────────────────────────────────────────────────────────────
    if started and not game.done and not paused:
        tick_acc += dt
        if tick_acc >= game.speed_ms:
            tick_acc -= game.speed_ms
            game.move()

    # ── Draw ──────────────────────────────────────────────────────────────────
    screen.fill(BG)

    draw_hud(screen)

    # Canvas background + grid
    pygame.draw.rect(screen, (7, 13, 10),
                     (0, CANVAS_OY, WIDTH, HEIGHT))
    draw_grid(screen, 0, CANVAS_OY)
    pygame.draw.rect(screen, BORDER,
                     (0, CANVAS_OY, WIDTH, HEIGHT), 1)

    draw_food(screen, 0, CANVAS_OY)
    draw_snake(screen, 0, CANVAS_OY)
    draw_controls(screen, CTRL_OY)

    if not started:
        draw_start_screen(screen, CANVAS_OY)
    elif game.done:
        draw_game_over(screen, CANVAS_OY)
    elif paused:
        draw_pause(screen, CANVAS_OY)

    pygame.display.flip()
    clock.tick(60)   # render at 60 fps; game logic runs at its own rate

pygame.quit()
sys.exit()