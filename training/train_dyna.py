import time
from game.snake import SnakeGame
from agents.dyna_q import DynaQAgent


def get_reward(game, prev_head, new_head):
    food = game.food

    # death
    if not game.dyna_alive:
        return -20

    # food eaten
    if new_head == food:
        return 15

    # distance shaping
    old_dist = abs(prev_head[0] - food[0]) + abs(prev_head[1] - food[1])
    new_dist = abs(new_head[0] - food[0]) + abs(new_head[1] - food[1])

    if new_dist < old_dist:
        return 1
    else:
        return -1


def train():
    agent = DynaQAgent()

    episodes = 3000

    for episode in range(episodes):

        game = SnakeGame()
        game.reset()

        state = game.get_state_dyna()

        total_reward = 0
        step = 0

        while game.dyna_alive and step < 1000:

            prev_head = game.dyna_ai[0]   # ✅ IMPORTANT FIX

            action = agent.choose_action(state)

            game.dyna_dir = game.get_new_direction(game.dyna_dir, action)

            old_state = state
            old_action = action

            game.move()

            new_head = game.dyna_ai[0]    # ✅ IMPORTANT FIX

            state = game.get_state_dyna()

            reward = get_reward(game, prev_head, new_head)

            total_reward += reward

            agent.update(old_state, old_action, reward, state)

            step += 1

        if episode % 100 == 0:
            print(f"[DYNA] Episode {episode} | Score: {game.dyna_score} | Reward: {total_reward:.2f}")

    agent.save("models/dyna_q.pkl")
    print("Dyna-Q training completed!")


if __name__ == "__main__":
    train()