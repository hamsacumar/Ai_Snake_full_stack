import time
import numpy as np

from game.snake import SnakeGame
from agents.qlearning import QLearningAgent


def get_reward(game):
    # death penalty
    if not game.ai_alive:
        return -10

    # food reward
    if game.ai[0] == game.food:
        return 10

    return -0.1


def train():
    agent = QLearningAgent()

    # load previous training if exists
    agent.load()

    episodes = 5000

    for episode in range(episodes):

        game = SnakeGame()
        game.reset()

        state = game.get_ai_state()
        total_reward = 0

        step = 0

        while game.ai_alive and step < 1000:

            # choose action
            action = agent.choose_action(state)

            # apply action → update direction
            game.ai_dir = game.get_new_direction(game.ai_dir, action)

            # store old state/action
            old_state = state
            old_action = action

            # move game (AI + human ignored)
            game.move()

            # new state
            state = game.get_ai_state()

            # reward
            reward = get_reward(game)
            total_reward += reward

            # Q-learning update
            agent.update(old_state, old_action, reward, state)

            step += 1

        # decay exploration slowly
        agent.decay_epsilon()

        # save model every 100 episodes
        if episode % 100 == 0:
            agent.save()
            print(f"Episode {episode} | Score: {game.ai_score} | Reward: {total_reward:.2f}")

    # final save
    agent.save()
    print("Training completed!")


if __name__ == "__main__":
    train()