import random
import numpy as np
import pickle
import os


class QLearningAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.q_table = {}

        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

    # =========================
    # Q VALUE ACCESS
    # =========================
    def get_q(self, state):
        if state not in self.q_table:
            self.q_table[state] = np.zeros(3, dtype=float)
        return self.q_table[state]

    # =========================
    # ACTION SELECTION
    # =========================
    def choose_action(self, state):
        # exploration
        if random.random() < self.epsilon:
            return random.randint(0, 2)

        # exploitation
        return int(np.argmax(self.get_q(state)))

    # =========================
    # Q UPDATE RULE
    # =========================
    def update(self, state, action, reward, next_state):
        q = self.get_q(state)
        next_q = self.get_q(next_state)

        q[action] = q[action] + self.alpha * (
            reward + self.gamma * np.max(next_q) - q[action]
        )

    # =========================
    # SAVE MODEL
    # =========================
    def save(self, filename="models/qlearning.pkl"):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as f:
            pickle.dump(self.q_table, f)

    # =========================
    # LOAD MODEL
    # =========================
    def load(self, filename="models/qlearning.pkl"):
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                self.q_table = pickle.load(f)

    # =========================
    # OPTIONAL: DECAY EXPLORATION
    # =========================
    def decay_epsilon(self, decay=0.995, min_epsilon=0.01):
        self.epsilon = max(min_epsilon, self.epsilon * decay)