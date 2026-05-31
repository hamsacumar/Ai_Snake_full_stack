import random

CELL = 20
COLS = 28
ROWS = 18
WIDTH = COLS * CELL   # 560
HEIGHT = ROWS * CELL  # 360


class SnakeGame:
    def __init__(self):
        self.best = 0
        self.reset()

    def reset(self):
        self.snake = [(5, 9), (4, 9), (3, 9)]   # (col, row) grid coords
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        self.food = self._spawn_food()
        self.score = 0
        self.done = False

    def _spawn_food(self):
        snake_set = set(self.snake)
        while True:
            pos = (random.randrange(COLS), random.randrange(ROWS))
            if pos not in snake_set:
                return pos

    def change_direction(self, new_dir):
        # prevent 180° reversal
        if (new_dir[0] == -self.direction[0] and new_dir[1] == -self.direction[1]):
            return
        self.next_direction = new_dir

    def move(self):
        if self.done:
            return

        self.direction = self.next_direction
        hx, hy = self.snake[0]
        new_head = (
            (hx + self.direction[0]) % COLS,
            (hy + self.direction[1]) % ROWS,
        )

        # self collision
        if new_head in self.snake:
            self.done = True
            if self.score > self.best:
                self.best = self.score
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.food = self._spawn_food()
        else:
            self.snake.pop()

    @property
    def speed_ms(self):
        """Tick interval in milliseconds — decreases as score rises."""
        if self.score < 5:
            return 140
        if self.score < 10:
            return 115
        if self.score < 20:
            return 90
        if self.score < 35:
            return 72
        return 58