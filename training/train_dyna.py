import time

from game.snake import SnakeGame
from agents.dyna_q import DynaQAgent


def get_reward(game):
    if not game.dyna_alive:
        return -10

    if game.dyna_ai[0] == game.food:
        return 10

    return -0.1


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

            action = agent.choose_action(state)

            game.dyna_dir = game.get_new_direction(game.dyna_dir, action)

            old_state = state
            old_action = action

            game.move()

            state = game.get_state_dyna()

            reward = get_reward(game)
            total_reward += reward

            agent.update(old_state, old_action, reward, state)

            step += 1

        if episode % 100 == 0:
            print(f"[DYNA] Episode {episode} | Score: {game.dyna_score} | Reward: {total_reward:.2f}")

    agent.save("models/dyna_q.pkl")
    print("Dyna-Q training completed!")


if __name__ == "__main__":
    train()