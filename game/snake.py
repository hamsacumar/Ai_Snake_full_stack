import random

CELL_SIZE = 20
WIDTH = 600
HEIGHT = 400


class SnakeGame:
    def __init__(self):
        self.reset()

    def get_state_q(self):
        return self.get_state(self.q_ai, self.q_dir)

    def get_state_dyna(self):
        return self.get_state(self.dyna_ai, self.dyna_dir)

    def get_state(self, snake, direction):
        head = snake[0]

        def danger(pos):
            return (
                    pos in self.human or
                    pos in self.q_ai or
                    pos in self.dyna_ai
            )

        straight = (head[0] + direction[0], head[1] + direction[1])
        left = (-direction[1], direction[0])
        right = (direction[1], -direction[0])

        food_up = self.food[1] < head[1]
        food_down = self.food[1] > head[1]
        food_left = self.food[0] < head[0]
        food_right = self.food[0] > head[0]

        return (
            int(danger(straight)),
            int(danger(left)),
            int(danger(right)),
            int(food_up),
            int(food_down),
            int(food_left),
            int(food_right)
        )

    def reset(self):
        # HUMAN
        self.human = [(100, 100)]
        self.human_dir = (CELL_SIZE, 0)
        self.human_score = 0
        self.human_alive = True

        # Q-LEARNING AI
        self.q_ai = [(400, 300)]
        self.q_dir = (-CELL_SIZE, 0)
        self.q_score = 0
        self.q_alive = True

        # DYNA-Q AI
        self.dyna_ai = [(300, 300)]
        self.dyna_dir = (CELL_SIZE, 0)
        self.dyna_score = 0
        self.dyna_alive = True

        self.food = self.spawn_food()

    def spawn_food(self):
        return (
            random.randrange(0, WIDTH, CELL_SIZE),
            random.randrange(0, HEIGHT, CELL_SIZE)
        )

    # =========================
    # MOVE ONE SNAKE
    # =========================
    def move_snake(self, snake, direction, snake_type):
        head = snake[0]

        new_head = (head[0] + direction[0], head[1] + direction[1])
        new_head = self.wrap(new_head)

        snake.insert(0, new_head)

        if new_head == self.food:
            if snake_type == "human":
                self.human_score += 1
            elif snake_type == "q":
                self.q_score += 1
            else:
                self.dyna_score += 1

            self.food = self.spawn_food()
        else:
            snake.pop()

        self.check_collision(snake, snake_type)

    # =========================
    # WRAP WORLD
    # =========================
    def wrap(self, pos):
        x, y = pos

        if x < 0:
            x = WIDTH - CELL_SIZE
        elif x >= WIDTH:
            x = 0

        if y < 0:
            y = HEIGHT - CELL_SIZE
        elif y >= HEIGHT:
            y = 0

        return (x, y)

    # =========================
    # COLLISION
    # =========================
    def check_collision(self, snake, snake_type):
        head = snake[0]

        if head in snake[1:]:
            self.kill(snake_type)

        if head in self.human and snake_type != "human":
            self.kill(snake_type)

        if head in self.q_ai and snake_type != "q":
            self.kill(snake_type)

        if head in self.dyna_ai and snake_type != "dyna":
            self.kill(snake_type)

    def kill(self, snake_type):
        if snake_type == "human":
            self.human_alive = False
        elif snake_type == "q":
            self.q_alive = False
        else:
            self.dyna_alive = False

    def get_new_direction(self, direction, action):
        # action: 0 = straight, 1 = left, 2 = right

        if action == 0:
            return direction
        elif action == 1:
            return (-direction[1], direction[0])
        else:
            return (direction[1], -direction[0])

    def move(self):

        # HUMAN (ignored in training but safe)
        if self.human_alive:
            self.move_snake(self.human, self.human_dir, "human")

        # Q AI
        if self.q_alive:
            self.move_snake(self.q_ai, self.q_dir, "q")

        # DYNA AI
        if self.dyna_alive:
            self.move_snake(self.dyna_ai, self.dyna_dir, "dyna")