import random
import numpy as np
import os
import pickle

class DynaQAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1, planning_steps=10):
        self.q_table = {}
        self.model = []

        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.planning_steps = planning_steps

    def get_q(self, state):
        if state not in self.q_table:
            self.q_table[state] = np.zeros(3)
        return self.q_table[state]

    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, 2)
        return int(np.argmax(self.get_q(state)))

    def update(self, state, action, reward, next_state):
        q = self.get_q(state)
        next_q = self.get_q(next_state)

        q[action] += self.alpha * (
            reward + self.gamma * np.max(next_q) - q[action]
        )

        # store experience for planning
        self.model.append((state, action, reward, next_state))

        # planning step (IMAGINARY LEARNING)
        self.planning()

    def planning(self):
        if len(self.model) == 0:
            return

        for _ in range(self.planning_steps):
            s, a, r, s2 = random.choice(self.model)
            q = self.get_q(s)
            next_q = self.get_q(s2)

            q[a] += self.alpha * (
                r + self.gamma * np.max(next_q) - q[a]
            )

    def save(self, filename="models/dyna_q.pkl"):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as f:
            pickle.dump({
                "q_table": self.q_table,
                "model": self.model
            }, f)

    def load(self, filename="models/dyna_q.pkl"):
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                data = pickle.load(f)

            self.q_table = data["q_table"]
            self.model = data["model"]