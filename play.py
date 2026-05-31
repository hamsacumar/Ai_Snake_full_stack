"""
Snake Arena  —  Retro-Cyberpunk Edition
Human vs Q-Learning vs Dyna-Q

Controls:
  Arrow keys  — steer your snake
  R           — reset round
  Q / Esc     — quit
"""

import math
import sys
import pygame
from game.snake import SnakeGame
from agents.qlearning import QLearningAgent
from agents.dyna_q import DynaQAgent

# ── Bootstrap ─────────────────────────────────────────────────────────────────
pygame.init()

CELL = 20

# Canvas where the snakes live (matches snake.py exactly — pixel coords unchanged)
ARENA_W = 800
ARENA_H = 650

# Chrome dimensions  ← BIGGER than before
SIDE_W = 260          # right panel (was 180)
TOP_H  = 80           # top bar     (was 56)
BOT_H  = 50           # bottom bar  (was 36)

WIN_W = ARENA_W + SIDE_W    # 860
WIN_H = TOP_H + ARENA_H + BOT_H  # 530

screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("SNAKE ARENA")
clock  = pygame.time.Clock()

# ── Palette ───────────────────────────────────────────────────────────────────
BG        = (  4,  8, 14)
ARENA_BG  = (  6, 13, 10)
GRID_COL  = ( 14, 30, 20)
PANEL_BG  = (  8, 14, 24)
BORDER    = ( 32, 68, 50)

PLAYER = {
    "human": {
        "name" : "HUMAN",
        "fill" : ( 20, 255, 120),
        "dim"  : (  8,  90,  45),
        "head" : (160, 255, 200),
        "label": ( 20, 255, 120),
        "dead" : ( 28,  65,  46),
    },
    "q": {
        "name" : "Q-AI",
        "fill" : ( 80, 160, 255),
        "dim"  : ( 20,  50, 110),
        "head" : (180, 220, 255),
        "label": ( 80, 160, 255),
        "dead" : ( 22,  38,  68),
    },
    "dyna": {
        "name" : "DYNA-AI",
        "fill" : (210,  60, 255),
        "dim"  : ( 72,  18,  94),
        "head" : (235, 160, 255),
        "label": (210,  60, 255),
        "dead" : ( 58,  16,  72),
    },
}

FOOD_COL   = (255,  55,  90)
FOOD_SHINE = (255, 170, 185)
WHITE      = (255, 255, 255)
MUTED      = ( 90, 120, 100)
TITLE_COL  = ( 55, 230, 145)
GOLD       = (255, 220,  55)

# ── Fonts — all sizes bumped up ───────────────────────────────────────────────
def _font(size, bold=False):
    for name in ("Orbitron", "Consolas", "Lucida Console", "Courier New", "monospace"):
        try:
            return pygame.font.SysFont(name, size, bold=bold)
        except Exception:
            pass
    return pygame.font.Font(None, size)

f_title  = _font(28, bold=True)   # was 20
f_timer  = _font(22, bold=True)   # was 17
f_name   = _font(15, bold=True)   # was 10
f_score  = _font(42, bold=True)   # was 26
f_badge  = _font(13, bold=True)   # was 10
f_len    = _font(13)               # was 10
f_ctrl   = _font(15)              # was 11
f_over   = _font(32, bold=True)
f_sub    = _font(17)

# ── Agents ────────────────────────────────────────────────────────────────────
game    = SnakeGame()
q_agent = QLearningAgent()
d_agent = DynaQAgent()
q_agent.load("models/qlearning.pkl")
d_agent.load("models/dyna_q.pkl")

frame   = 0
elapsed = 0

def reset_game():
    global game, elapsed
    game    = SnakeGame()
    elapsed = 0

# ── Helpers ───────────────────────────────────────────────────────────────────
def ax(px): return px
def ay(py): return TOP_H + py

def draw_rounded_rect(surf, color, rect, radius=6, alpha=None):
    if alpha is not None:
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, alpha), s.get_rect(), border_radius=radius)
        surf.blit(s, rect.topleft)
    else:
        pygame.draw.rect(surf, color, rect, border_radius=radius)

# ── Draw: Grid ────────────────────────────────────────────────────────────────
def draw_grid():
    for c in range(0, ARENA_W + 1, CELL):
        pygame.draw.line(screen, GRID_COL, (ax(c), ay(0)), (ax(c), ay(ARENA_H)))
    for r in range(0, ARENA_H + 1, CELL):
        pygame.draw.line(screen, GRID_COL, (ax(0), ay(r)), (ax(ARENA_W), ay(r)))

# ── Draw: Food ────────────────────────────────────────────────────────────────
def draw_food():
    fx, fy = game.food
    cx = ax(fx) + CELL // 2
    cy = ay(fy) + CELL // 2
    pulse = 0.82 + 0.18 * math.sin(frame * 0.13)
    r = max(4, int(8 * pulse))
    pygame.draw.circle(screen, FOOD_COL, (cx, cy), r)
    pygame.draw.circle(screen, FOOD_SHINE, (cx - 2, cy - 2), max(1, r // 3))

# ── Draw: Snake ───────────────────────────────────────────────────────────────
def draw_snake(segments, palette, direction, alive):
    n = len(segments)
    for i, (sx, sy) in enumerate(segments):
        x  = ax(sx) + 1
        y  = ay(sy) + 1
        sz = CELL - 2
        is_head = (i == 0)

        if not alive:
            color  = palette["dead"]
            radius = 2
        elif is_head:
            color  = palette["head"]
            radius = 5
        else:
            t  = i / max(n - 1, 1)
            r_ = int(palette["fill"][0] * (1 - t * 0.45))
            g_ = int(palette["fill"][1] * (1 - t * 0.55))
            b_ = int(palette["fill"][2] * (1 - t * 0.30))
            color  = (r_, g_, b_)
            radius = 3

        pygame.draw.rect(screen, color, (x, y, sz, sz), border_radius=radius)

        if is_head and alive:
            dx, dy  = direction[0] // CELL, direction[1] // CELL
            eye_col = BG
            esz     = 3
            if dx == 1:
                eyes = [(x + sz - 6, y + 4), (x + sz - 6, y + sz - 7)]
            elif dx == -1:
                eyes = [(x + 3, y + 4), (x + 3, y + sz - 7)]
            elif dy == -1:
                eyes = [(x + 4, y + 3), (x + sz - 7, y + 3)]
            else:
                eyes = [(x + 4, y + sz - 6), (x + sz - 7, y + sz - 6)]
            for ex, ey in eyes:
                pygame.draw.rect(screen, eye_col, (ex, ey, esz, esz))

# ── Draw: Top bar ─────────────────────────────────────────────────────────────
def draw_top_bar():
    pygame.draw.rect(screen, (6, 12, 22), (0, 0, WIN_W, TOP_H))
    pygame.draw.line(screen, BORDER, (0, TOP_H - 1), (WIN_W, TOP_H - 1))

    title = f_title.render("SNAKE  ARENA", True, TITLE_COL)
    screen.blit(title, title.get_rect(centerx=ARENA_W // 2, centery=TOP_H // 2))

    secs  = elapsed // 1000
    timer = f_timer.render(f"{secs:04d}s", True, MUTED)
    screen.blit(timer, timer.get_rect(right=ARENA_W - 12, centery=TOP_H // 2))

# ── Draw: Bottom bar ──────────────────────────────────────────────────────────
def draw_bot_bar():
    by = TOP_H + ARENA_H
    pygame.draw.rect(screen, (5, 10, 18), (0, by, WIN_W, BOT_H))
    pygame.draw.line(screen, BORDER, (0, by), (WIN_W, by))
    hint = f_ctrl.render("↑↓←→  Steer     R  Reset     Q  Quit", True, MUTED)
    screen.blit(hint, hint.get_rect(centerx=WIN_W // 2, centery=by + BOT_H // 2))

# ── Draw: Side panel ─────────────────────────────────────────────────────────
def draw_side_panel():
    px = ARENA_W
    pygame.draw.rect(screen, PANEL_BG, (px, 0, SIDE_W, WIN_H))
    pygame.draw.line(screen, BORDER, (px, 0), (px, WIN_H))

    pcx = px + SIDE_W // 2    # panel centre-x
    y   = TOP_H + 22

    players = [
        ("human", game.human,   game.human_alive, game.human_score),
        ("q",     game.q_ai,    game.q_alive,      game.q_score),
        ("dyna",  game.dyna_ai, game.dyna_alive,   game.dyna_score),
    ]

    for key, snake, alive, score_ in players:
        p = PLAYER[key]

        # coloured top stripe
        stripe_col = p["fill"] if alive else p["dead"]
        pygame.draw.rect(screen, stripe_col,
                         (px + 14, y, SIDE_W - 28, 4), border_radius=2)
        y += 14

        # player name
        name_surf = f_name.render(p["name"], True, p["label"] if alive else MUTED)
        screen.blit(name_surf, name_surf.get_rect(centerx=pcx, top=y))
        y += 24

        # big score
        sc_col  = p["fill"] if alive else p["dead"]
        sc_surf = f_score.render(f"{score_:02d}", True, sc_col)
        screen.blit(sc_surf, sc_surf.get_rect(centerx=pcx, top=y))
        y += 52

        # status badge
        if alive:
            badge_text = "● ALIVE"
            badge_fg   = p["fill"]
            badge_bg   = p["dim"]
            badge_a    = 230
        else:
            badge_text = "✕  DEAD"
            badge_fg   = (255, 65, 85)
            badge_bg   = (55, 10, 16)
            badge_a    = 230

        bw, bh = 110, 26
        bx = pcx - bw // 2
        draw_rounded_rect(screen, badge_bg,
                          pygame.Rect(bx, y, bw, bh), radius=13, alpha=badge_a)
        b_surf = f_badge.render(badge_text, True, badge_fg)
        screen.blit(b_surf, b_surf.get_rect(centerx=pcx, centery=y + bh // 2))
        y += 38

        # length row
        ln_lbl = f_len.render("LEN", True, MUTED)
        length  = len(snake) if alive else 0
        ln_val  = f_len.render(f"{length:03d}", True, p["label"] if alive else MUTED)
        screen.blit(ln_lbl, ln_lbl.get_rect(right=pcx - 8,  centery=y + 8))
        screen.blit(ln_val, ln_val.get_rect(left=pcx + 8,   centery=y + 8))
        y += 28

        # divider
        pygame.draw.line(screen, BORDER,
                         (px + 20, y), (px + SIDE_W - 20, y))
        y += 20

    # colour swatches legend at bottom
    sw_y = TOP_H + ARENA_H - 80
    for key in ("human", "q", "dyna"):
        p = PLAYER[key]
        pygame.draw.rect(screen, p["fill"],
                         (px + 20, sw_y + 2, 12, 12), border_radius=3)
        sw_lbl = f_len.render(p["name"], True, MUTED)
        screen.blit(sw_lbl, (px + 40, sw_y))
        sw_y += 22

# ── Reset button ─────────────────────────────────────────────────────────────
BTN_RESET = pygame.Rect(ARENA_W + 24, 18, SIDE_W - 48, 36)

def draw_reset_button():
    mouse = pygame.mouse.get_pos()
    hover = BTN_RESET.collidepoint(mouse)
    col   = (0, 200, 90) if hover else (0, 130, 55)
    pygame.draw.rect(screen, col, BTN_RESET, border_radius=8)
    lbl = f_badge.render("R  RESET", True, WHITE)
    screen.blit(lbl, lbl.get_rect(center=BTN_RESET.center))

# ── All-dead overlay ─────────────────────────────────────────────────────────
def draw_all_dead_banner():
    ovl = pygame.Surface((ARENA_W, ARENA_H), pygame.SRCALPHA)
    ovl.fill((4, 8, 14, 210))
    screen.blit(ovl, (0, TOP_H))

    cy = TOP_H + ARENA_H // 2

    results = sorted(
        [("HUMAN", game.human_score),
         ("Q-AI",  game.q_score),
         ("DYNA",  game.dyna_score)],
        key=lambda x: -x[1]
    )
    winner, wsc = results[0]

    big  = f_over.render(f"{winner}  WINS  —  {wsc:02d} pts", True, GOLD)
    hint = f_sub.render("Press  R  to play again", True, MUTED)
    screen.blit(big,  big.get_rect(centerx=ARENA_W // 2, centery=cy - 22))
    screen.blit(hint, hint.get_rect(centerx=ARENA_W // 2, centery=cy + 20))

# ── Main loop ─────────────────────────────────────────────────────────────────
prev_ms = pygame.time.get_ticks()
running = True

while running:
    now_ms  = pygame.time.get_ticks()
    dt      = now_ms - prev_ms
    prev_ms = now_ms
    frame  += 1

    all_dead = not game.human_alive and not game.q_alive and not game.dyna_alive
    if not all_dead:
        elapsed += dt

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_q, pygame.K_ESCAPE):
                running = False
            if event.key == pygame.K_r:
                reset_game()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if BTN_RESET.collidepoint(event.pos):
                reset_game()

    # Human input
    keys = pygame.key.get_pressed()
    if game.human_alive:
        if keys[pygame.K_UP]:
            game.human_dir = (0, -CELL)
        elif keys[pygame.K_DOWN]:
            game.human_dir = (0, CELL)
        elif keys[pygame.K_LEFT]:
            game.human_dir = (-CELL, 0)
        elif keys[pygame.K_RIGHT]:
            game.human_dir = (CELL, 0)

    # Agent actions
    if game.q_alive:
        state = game.get_state_q()
        action = q_agent.choose_action(state)
        game.q_dir = game.get_new_direction(game.q_dir, action)

    if game.dyna_alive:
        state = game.get_state_dyna()
        action = d_agent.choose_action(state)
        game.dyna_dir = game.get_new_direction(game.dyna_dir, action)

    # Step
    game.step_all()

    # Draw
    screen.fill(BG)
    pygame.draw.rect(screen, ARENA_BG, (0, TOP_H, ARENA_W, ARENA_H))

    draw_grid()
    draw_food()
    draw_snake(game.human,   PLAYER["human"], game.human_dir, game.human_alive)
    draw_snake(game.q_ai,    PLAYER["q"],     game.q_dir,     game.q_alive)
    draw_snake(game.dyna_ai, PLAYER["dyna"],  game.dyna_dir,  game.dyna_alive)

    pygame.draw.rect(screen, BORDER, (0, TOP_H, ARENA_W, ARENA_H), 1)

    draw_top_bar()
    draw_bot_bar()
    draw_side_panel()
    draw_reset_button()

    if all_dead:
        draw_all_dead_banner()

    pygame.display.flip()
    clock.tick(10)

pygame.quit()
sys.exit()