from random import choice, randint

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
CENTER_POSITION = (GRID_WIDTH // 2 * GRID_SIZE, GRID_HEIGHT // 2 * GRID_SIZE)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
BOARD_BACKGROUND_COLOR = (30, 30, 30)
BORDER_COLOR = (220, 220, 220)
APPLE_COLOR = (229, 57, 53)
SNAKE_COLOR = (76, 175, 80)
BOULDER_COLOR = (120, 120, 120)
SPEED = 10
OPPOSITES = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
OBSTACLE_AMOUNT = 5


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

pygame.display.set_caption('The Snake')

clock = pygame.time.Clock()


def handle_keys() -> tuple[int, int] | None:
    """Обработка нажатий клавиш пользователя."""
    direction = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit

            if event.key == pygame.K_UP:
                direction = UP
            elif event.key == pygame.K_DOWN:
                direction = DOWN
            elif event.key == pygame.K_LEFT:
                direction = LEFT
            elif event.key == pygame.K_RIGHT:
                direction = RIGHT

    return direction


class GameObject():
    """Базовый класс для всех игровых объектов."""

    def __init__(
        self,
        position: tuple[int, int] = CENTER_POSITION,
        body_color: tuple[int, int, int] = (0, 0, 0)
    ) -> None:
        self.position = position
        self.body_color = body_color

    def randomize_position(
        self,
        width: int = GRID_WIDTH,
        height: int = GRID_HEIGHT,
        size: int = GRID_SIZE,
        ban_positions: set[tuple[int, int]] | None = None,
    ) -> tuple[int, int]:
        """Назначает случайную допустимую позицию объекту и возвращает её."""
        if ban_positions is None:
            ban_positions = set()

        while True:
            pos = (randint(0, width - 1) * size, randint(0, height - 1) * size)
            if pos not in ban_positions:
                self.position = pos
                return pos

    def draw(self) -> None:
        """Отрисовка объекта."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс для объекта 'яблоко'. При подборе увеличивает длину змейки."""

    def __init__(self) -> None:
        super().__init__((0, 0), APPLE_COLOR)
        self.randomize_position()


class Obstacle(GameObject):
    """Статическое препятствие, вызывающее проигрыш при столкновении."""

    def __init__(self) -> None:
        super().__init__((0, 0), BOULDER_COLOR)
        self.randomize_position(ban_positions={CENTER_POSITION})


class Snake(GameObject):
    """Класс для объекта 'змейка'."""

    def __init__(self) -> None:
        super().__init__(CENTER_POSITION, SNAKE_COLOR)
        self.length: int = 1
        self.positions: list[tuple[int, int]] = [self.position]
        self.direction: tuple[int, int] = RIGHT
        self.next_direction: tuple[int, int] | None = None
        self.last: tuple[int, int] | None = None

    def get_head_position(self) -> tuple[int, int]:
        """Возвращает первый сегмент змейки."""
        return self.positions[0]

    def move(self) -> None:
        """Перемещает змейку на одну клетку и обновляет её тело."""
        x, y = self.get_head_position()

        new_x = (x + self.direction[0] * GRID_SIZE) % SCREEN_WIDTH
        new_y = (y + self.direction[1] * GRID_SIZE) % SCREEN_HEIGHT

        self.positions.insert(0, (new_x, new_y))

        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def set_direction(self, direction: tuple[int, int] | None) -> None:
        """
        Устанавливаем направление движения змейки, если оно не
        противоположно текущему.
        """
        if direction and direction != OPPOSITES[self.direction]:
            self.next_direction = direction

    def update_direction(self) -> None:
        """Обновляет текущее направление движения, если оно было изменено."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def reset(self) -> None:
        """Восстановление начального состояния змейки."""
        self.length = 1
        self.position = CENTER_POSITION
        self.positions = [CENTER_POSITION]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None

    def draw(self):
        """Отрисовка змейки на экране."""
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


def main():
    """Основной игровой цикл."""
    # Инициализация pygame и экземпляров классов
    pygame.init()
    apple = Apple()
    snake = Snake()
    obstacles = [Obstacle() for _ in range(OBSTACLE_AMOUNT)]

    while True:

        # Ввод
        direction = handle_keys()
        snake.set_direction(direction)

        # Обновление состояния игры
        snake.update_direction()
        snake.move()

        # Столкновение с яблоком
        if snake.get_head_position() == apple.position:
            snake.length += 1
            ban = set(snake.positions + [o.position for o in obstacles])
            apple.randomize_position(ban_positions=ban)

        # Столкновение змейки с собой
        if snake.get_head_position() in snake.positions[1:]:
            obstacles = [Obstacle() for _ in range(OBSTACLE_AMOUNT)]
            snake.reset()

        # Столкновение с препятствием
        if snake.get_head_position() in {o.position for o in obstacles}:
            obstacles = [Obstacle() for _ in range(OBSTACLE_AMOUNT)]
            snake.reset()

        # Отрисовка
        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        for boulder in obstacles:
            boulder.draw()

        pygame.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
