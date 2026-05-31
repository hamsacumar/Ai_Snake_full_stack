import numpy as np

from game.snake import SnakeGame
from agents.qlearning import QLearningAgent


def get_reward(game, prev_head, new_head):
    food = game.food

    # death
    if not game.q_alive:
        return -20

    # food eaten
    if new_head == food:
        return 20

    # distance shaping
    old_dist = abs(prev_head[0] - food[0]) + abs(prev_head[1] - food[1])
    new_dist = abs(new_head[0] - food[0]) + abs(new_head[1] - food[1])

    return (old_dist - new_dist) * 0.2 - 0.05


def train():
    agent = QLearningAgent()
    agent.load("models/qlearning.pkl")

    episodes = 5000

    for episode in range(episodes):

        game = SnakeGame()
        game.reset()

        state = game.get_state_q()

        total_reward = 0
        step = 0

        while game.q_alive and step < 1000:

            prev_head = game.q_ai[0]

            action = agent.choose_action(state)

            game.q_dir = game.get_new_direction(game.q_dir, action)

            old_state = state

            game.move()

            new_head = game.q_ai[0]

            state = game.get_state_q()

            reward = get_reward(game, prev_head, new_head)

            agent.update(old_state, action, reward, state)

            total_reward += reward
            step += 1

        agent.decay_epsilon()

        if episode % 100 == 0:
            agent.save("models/qlearning.pkl")
            print(f"Episode {episode} | Score: {game.q_score} | Reward: {total_reward:.2f}")

    agent.save("models/qlearning.pkl")
    print("Training completed!")


if __name__ == "__main__":
    train()