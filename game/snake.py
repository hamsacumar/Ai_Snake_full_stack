import random

CELL_SIZE = 20
WIDTH = 600
HEIGHT = 400


class SnakeGame:
    def __init__(self):
        self.reset()

    # =========================
    # RESET GAME
    # =========================
    def reset(self):
        # Human snake
        self.human = [(100, 100)]
        self.human_dir = (CELL_SIZE, 0)
        self.human_score = 0
        self.human_alive = True

        # AI snake
        self.ai = [(400, 300)]
        self.ai_dir = (-CELL_SIZE, 0)
        self.ai_score = 0
        self.ai_alive = True

        self.food = self.spawn_food()

        # RL tracking
        self.ai_last_state = None
        self.ai_last_action = None

    # =========================
    # FOOD
    # =========================
    def spawn_food(self):
        return (
            random.randrange(0, WIDTH, CELL_SIZE),
            random.randrange(0, HEIGHT, CELL_SIZE)
        )

    # =========================
    # HUMAN CONTROL
    # =========================
    def change_human_dir(self, new_dir):
        if (new_dir[0] * -1, new_dir[1] * -1) == self.human_dir:
            return
        self.human_dir = new_dir

    # =========================
    # MAIN UPDATE LOOP
    # =========================
    def move(self):
        if self.human_alive:
            self.move_snake("human")

        if self.ai_alive:
            self.move_snake("ai")

    # =========================
    # MOVE SINGLE SNAKE
    # =========================
    def move_snake(self, snake_type):

        if snake_type == "human":
            snake = self.human
            direction = self.human_dir
        else:
            snake = self.ai
            direction = self.ai_dir

        head_x, head_y = snake[0]

        new_head = (head_x + direction[0], head_y + direction[1])
        new_head = self.wrap(new_head)

        snake.insert(0, new_head)

        # food check
        if new_head == self.food:
            if snake_type == "human":
                self.human_score += 1
            else:
                self.ai_score += 1

            self.food = self.spawn_food()
        else:
            snake.pop()

        self.check_collision(snake_type, new_head)

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
    # COLLISIONS
    # =========================
    def check_collision(self, snake_type, head):

        if snake_type == "human":
            snake = self.human
            other = self.ai
        else:
            snake = self.ai
            other = self.human

        # self collision
        if head in snake[1:]:
            if snake_type == "human":
                self.human_alive = False
            else:
                self.ai_alive = False

        # collision with other snake
        if head in other:
            if snake_type == "human":
                self.human_alive = False
            else:
                self.ai_alive = False

    # =========================
    # RL STATE (AI OBSERVATION)
    # =========================
    def get_ai_state(self):
        head = self.ai[0]

        dir_l = self.turn_left(self.ai_dir)
        dir_r = self.turn_right(self.ai_dir)
        dir_s = self.ai_dir

        danger_straight = self.is_danger(head, dir_s, self.ai, self.human)
        danger_left = self.is_danger(head, dir_l, self.ai, self.human)
        danger_right = self.is_danger(head, dir_r, self.ai, self.human)

        food_up = self.food[1] < head[1]
        food_down = self.food[1] > head[1]
        food_left = self.food[0] < head[0]
        food_right = self.food[0] > head[0]

        return (
            int(danger_straight),
            int(danger_left),
            int(danger_right),
            int(food_up),
            int(food_down),
            int(food_left),
            int(food_right)
        )

    # =========================
    # RL ACTION HANDLING
    # =========================
    def get_new_direction(self, direction, action):
        # 0 = straight
        # 1 = left
        # 2 = right

        if action == 0:
            return direction
        elif action == 1:
            return self.turn_left(direction)
        else:
            return self.turn_right(direction)

    def ai_move_logic(self, agent):
        state = self.get_ai_state()

        action = agent.choose_action(state)

        self.ai_dir = self.get_new_direction(self.ai_dir, action)

        self.ai_last_state = state
        self.ai_last_action = action

    # =========================
    # RL REWARD
    # =========================
    def get_ai_reward(self):
        if not self.ai_alive:
            return -10

        if self.ai[0] == self.food:
            return 10

        return -0.1

    # =========================
    # HELPERS
    # =========================
    def turn_left(self, direction):
        return (-direction[1], direction[0])

    def turn_right(self, direction):
        return (direction[1], -direction[0])

    def is_danger(self, head, direction, snake_self, snake_other):
        x, y = head
        dx, dy = direction

        nx = x + dx
        ny = y + dy

        if nx < 0 or nx >= WIDTH or ny < 0 or ny >= HEIGHT:
            return True

        if (nx, ny) in snake_self:
            return True

        if (nx, ny) in snake_other:
            return True

        return False