from random import choice, randint

import pygame as pg

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
DEFAULT_COLOR = (0, 0, 0)
APPLE_COLOR = (229, 57, 53)
APPLE_BORD_COLOR = (139, 0, 0)
SNAKE_COLOR = (76, 175, 80)
SNAKE_BORD_COLOR = (27, 94, 32)
OBSTACLE_COLOR = (120, 120, 120)
OBSTACLE_BORD_COLOR = (60, 60, 60)

SPEED = 10

OPPOSITES = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
OBSTACLE_AMOUNT = 5


screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('The Snake')
clock = pg.time.Clock()


def handle_keys() -> tuple[int, int] | None:
    """Обработка нажатий клавиш пользователя."""
    direction = None

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit

            if event.key == pg.K_UP:
                direction = UP
            elif event.key == pg.K_DOWN:
                direction = DOWN
            elif event.key == pg.K_LEFT:
                direction = LEFT
            elif event.key == pg.K_RIGHT:
                direction = RIGHT

    return direction


class GameObject():
    """Базовый класс для всех игровых объектов."""

    def __init__(
            self,
            body_color=DEFAULT_COLOR,
            border_color=DEFAULT_COLOR
    ) -> None:
        self.position: tuple[int, int] = CENTER_POSITION
        self.body_color: tuple[int, int, int] = body_color
        self.border_color: tuple[int, int, int] = border_color

    def draw_cell(self) -> None:
        """Отрисовывает объект в виде одной клетки (GRID_SIZE x GRID_SIZE)."""
        rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, self.border_color, rect, 1)

    def draw(self) -> None:
        """Базовый метод отрисовки."""
        self.draw_cell()


class Apple(GameObject):
    """Класс для объекта 'яблоко'. При подборе увеличивает длину змейки."""

    def __init__(
        self,
        body_color: tuple[int, int, int] = APPLE_COLOR,
        border_color: tuple[int, int, int] = APPLE_BORD_COLOR,
        ban_position: tuple[int, int] = CENTER_POSITION
    ) -> None:
        super().__init__(body_color, border_color)
        self.randomize_position(ban_position)

    def randomize_position(
            self,
            positions_taken: set[tuple[int, int]]
    ) -> None:
        """Назначает случайную допустимую позицию и возвращает её."""
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if self.position not in positions_taken:
                break

    def draw(self) -> None:
        """Отрисовка яблока."""
        self.draw_cell()


class Snake(GameObject):
    """Класс для объекта 'змейка'."""

    def __init__(
        self,
        body_color: tuple[int, int, int] = SNAKE_COLOR,
        border_color: tuple[int, int, int] = SNAKE_BORD_COLOR
    ) -> None:
        super().__init__(body_color, border_color)
        self.length: int = 1
        self.positions: list[tuple[int, int]] = [self.position]
        self.direction: tuple[int, int] = RIGHT
        self.next_direction: tuple[int, int] | None = None

    def get_head_position(self) -> tuple[int, int]:
        """Возвращает первый сегмент змейки."""
        return self.positions[0]

    def move(self) -> None:
        """Перемещает змейку на одну клетку и обновляет её тело."""
        x, y = self.get_head_position()
        dx, dy = self.direction

        new_x = (x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (y + dy * GRID_SIZE) % SCREEN_HEIGHT

        self.positions.insert(0, (new_x, new_y))

        if len(self.positions) > self.length:
            self.positions.pop()

    def update_direction(self, direction: tuple[int, int] | None) -> None:
        """
        Обновляем направление движения змейки, если оно не
        противоположно текущему.
        """
        # примаем ввод пользователя
        if direction and direction != OPPOSITES[self.direction]:
            self.next_direction = direction
        # применяем накопленное направление
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def reset(self) -> None:
        """Восстановление начального состояния змейки."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])

    def draw(self) -> None:
        """Отрисовка змейки на экране."""
        for position in self.positions:
            self.position = position
            self.draw_cell()


def main():
    """Основной игровой цикл."""
    # Инициализация pygame и экземпляров классов
    pg.init()

    snake = Snake()
    apple = Apple()
    obstacles = []

    positions_taken = {CENTER_POSITION, apple.position}
    for _ in range(OBSTACLE_AMOUNT):
        obstacle = Apple(OBSTACLE_COLOR, OBSTACLE_BORD_COLOR)
        obstacle.randomize_position(positions_taken)
        obstacles.append(obstacle)
        positions_taken.add(obstacle.position)

    while True:

        # Ввод
        direction = handle_keys()

        # Обновление состояния игры
        snake.update_direction(direction)
        snake.move()

        # Столкновение с яблоком
        if snake.get_head_position() == apple.position:
            snake.length += 1

            apple.randomize_position(
                set(snake.positions) | {o.position for o in obstacles}
            )

        # Столкновение змейки с собой
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()

            apple.randomize_position(
                set(snake.positions) | {o.position for o in obstacles}
            )

            positions_taken = {CENTER_POSITION, apple.position}
            for o in obstacles:
                o.randomize_position(positions_taken)
                positions_taken.add(o.position)

        # Столкновение с препятствием
        elif snake.get_head_position() in {o.position for o in obstacles}:
            snake.reset()

            apple.randomize_position(
                set(snake.positions) | {o.position for o in obstacles}
            )

            positions_taken = {CENTER_POSITION, apple.position}
            for o in obstacles:
                o.randomize_position(positions_taken)
                positions_taken.add(o.position)

        # Отрисовка
        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        for o in obstacles:
            o.draw()

        pg.display.update()
        clock.tick(SPEED)


if __name__ == '__main__':
    main()
