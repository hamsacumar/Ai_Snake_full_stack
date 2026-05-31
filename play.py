import pygame
from game.snake import SnakeGame
from agents.qlearning import QLearningAgent
from agents.dyna_q import DynaQAgent

pygame.init()

CELL = 20
WIDTH, HEIGHT = 600, 400

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 20)

game = SnakeGame()

# ================= AGENTS =================
q_agent = QLearningAgent()
d_agent = DynaQAgent()

q_agent.load("models/qlearning.pkl")
d_agent.load("models/dyna_q.pkl")

running = True


def reset_game():
    global game
    game = SnakeGame()


while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # ================= GLOBAL CONTROLS =================
    if keys[pygame.K_q]:
        running = False

    if keys[pygame.K_r]:
        reset_game()

    # ================= HUMAN =================
    if game.human_alive:
        if keys[pygame.K_UP]:
            game.human_dir = (0, -CELL)
        elif keys[pygame.K_DOWN]:
            game.human_dir = (0, CELL)
        elif keys[pygame.K_LEFT]:
            game.human_dir = (-CELL, 0)
        elif keys[pygame.K_RIGHT]:
            game.human_dir = (CELL, 0)

    # ================= Q AI =================
    if game.q_alive:
        state = game.get_state_q()
        action = q_agent.choose_action(state)
        game.q_dir = game.get_new_direction(game.q_dir, action)

    # ================= DYNA AI =================
    if game.dyna_alive:
        state = game.get_state_dyna()
        action = d_agent.choose_action(state)
        game.dyna_dir = game.get_new_direction(game.dyna_dir, action)

    # ================= MOVE =================
    if game.human_alive:
        game.move_snake(game.human, game.human_dir, "human")

    if game.q_alive:
        game.move_snake(game.q_ai, game.q_dir, "q")

    if game.dyna_alive:
        game.move_snake(game.dyna_ai, game.dyna_dir, "dyna")

    # ================= AUTO RESET =================
    if not game.human_alive and not game.q_alive and not game.dyna_alive:
        reset_game()

    # ================= DRAW =================
    screen.fill((0, 0, 0))

    pygame.draw.rect(screen, (255, 0, 0), (*game.food, CELL, CELL))

    for s in game.human:
        pygame.draw.rect(screen, (0, 255, 0), (*s, CELL, CELL))

    for s in game.q_ai:
        pygame.draw.rect(screen, (0, 0, 255), (*s, CELL, CELL))

    for s in game.dyna_ai:
        pygame.draw.rect(screen, (200, 0, 255), (*s, CELL, CELL))

    # ================= HUD =================
    hud = font.render(
        f"Human: {game.human_score} | Q: {game.q_score} | Dyna: {game.dyna_score}",
        True,
        (255, 255, 255)
    )
    screen.blit(hud, (10, 10))

    pygame.display.flip()
    clock.tick(10)

pygame.quit()