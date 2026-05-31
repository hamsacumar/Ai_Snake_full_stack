import pygame

from game.snake import SnakeGame
from agents.qlearning import QLearningAgent

pygame.init()

CELL = 20
WIDTH, HEIGHT = 600, 400

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 24)

game = SnakeGame()

# =========================
# LOAD TRAINED AI
# =========================
agent = QLearningAgent()
agent.load("models/qlearning.pkl")

running = True


while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # =========================
    # GLOBAL CONTROLS
    # =========================
    if keys[pygame.K_q]:
        running = False

    if keys[pygame.K_r]:
        game.reset()

    # =========================
    # HUMAN CONTROL
    # =========================
    if game.human_alive:
        if keys[pygame.K_UP]:
            game.change_human_dir((0, -CELL))
        elif keys[pygame.K_DOWN]:
            game.change_human_dir((0, CELL))
        elif keys[pygame.K_LEFT]:
            game.change_human_dir((-CELL, 0))
        elif keys[pygame.K_RIGHT]:
            game.change_human_dir((CELL, 0))

    # =========================
    # AI CONTROL (TRAINED MODEL)
    # =========================
    if game.ai_alive:

        state = game.get_ai_state()
        action = agent.choose_action(state)

        game.ai_dir = game.get_new_direction(game.ai_dir, action)

        # optional: store last move (for future learning / debugging)
        game.ai_last_state = state
        game.ai_last_action = action

    # =========================
    # MOVE GAME
    # =========================
    game.move()

    # =========================
    # DRAWING
    # =========================
    screen.fill((0, 0, 0))

    # food
    pygame.draw.rect(screen, (255, 0, 0), (*game.food, CELL, CELL))

    # human snake
    for i, s in enumerate(game.human):
        color = (0, 255, 0) if game.human_alive else (80, 80, 80)
        pygame.draw.rect(screen, color, (*s, CELL, CELL))

    # AI snake
    for i, s in enumerate(game.ai):
        color = (0, 0, 255) if game.ai_alive else (80, 80, 80)
        pygame.draw.rect(screen, color, (*s, CELL, CELL))

    # =========================
    # SCORE
    # =========================
    text = font.render(
        f"Human: {game.human_score} | AI: {game.ai_score}",
        True,
        (255, 255, 255)
    )
    screen.blit(text, (10, 10))

    # =========================
    # STATUS
    # =========================
    status = font.render(
        f"Human: {'Alive' if game.human_alive else 'Dead'} | AI: {'AI (Q-Learning)'}",
        True,
        (200, 200, 200)
    )
    screen.blit(status, (10, 35))

    pygame.display.flip()
    clock.tick(10)

pygame.quit()