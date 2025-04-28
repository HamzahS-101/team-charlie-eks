import pygame

from entity import Entity
from utils import load_spritesheet


class Player(Entity):
    def __init__(self, rect) -> None:
        super().__init__(rect, "player")

        self.load_animations(
            [
                {
                    "name": "idle",
                    "images": load_spritesheet(f"{self.path}idle", [16] * 2),
                    "tags": ["loop"],
                    "colorkey": (255, 0, 0),
                },
                {
                    "name": "walk_left",
                    "images": load_spritesheet(f"{self.path}walk_left", [16] * 2),
                    "tags": ["loop"],
                    "colorkey": (255, 0, 0),
                },
                {
                    "name": "walk_right",
                    "images": load_spritesheet(f"{self.path}walk_right", [16] * 2),
                    "tags": ["loop"],
                    "colorkey": (255, 0, 0),
                },
                {
                    "name": "walk_up",
                    "images": load_spritesheet(f"{self.path}walk_up", [16] * 2),
                    "tags": ["loop"],
                    "colorkey": (255, 0, 0),
                },
                {
                    "name": "walk_down",
                    "images": load_spritesheet(f"{self.path}walk_down", [16] * 2),
                    "tags": ["loop"],
                    "colorkey": (255, 0, 0),
                },
            ]
        )

        self.run = False
        self.moving_right = False
        self.moving_left = False
        self.moving_up = False
        self.moving_down = False

        self.set_action("idle")

    def handle_keydown(self, key: int) -> None:
        if key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
            self.run = True

        if key in [pygame.K_d, pygame.K_RIGHT]:
            self.moving_right = True
        if key in [pygame.K_a, pygame.K_LEFT]:
            self.moving_left = True

        if key in [pygame.K_w, pygame.K_UP]:
            self.moving_up = True
        if key in [pygame.K_s, pygame.K_DOWN]:
            self.moving_down = True

        if key == pygame.K_SPACE:
            self.phase = not self.phase

    def handle_keyup(self, key: int) -> None:
        if key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
            self.run = False

        if key in [pygame.K_d, pygame.K_RIGHT]:
            self.moving_right = False
        if key in [pygame.K_a, pygame.K_LEFT]:
            self.moving_left = False

        if key in [pygame.K_w, pygame.K_UP]:
            self.moving_up = False
        if key in [pygame.K_s, pygame.K_DOWN]:
            self.moving_down = False

    def update(self, dt: float, tiles) -> None:
        self.update_frame(dt)

        movement = self.move(dt)

        collisons = self.move_and_collide(movement, tiles)

    def move(self, dt: float) -> tuple[float, float]:
        horizontal = self.moving_right or self.moving_left
        vertical = self.moving_up or self.moving_down

        speed = 50 * dt
        dx = 0
        dy = 0

        if horizontal and vertical:
            dx = 0.70710678118 * speed
            dy = 0.70710678118 * speed
        elif horizontal:
            dx = speed
        elif vertical:
            dy = speed

        if self.run:
            dx *= 2
            dy *= 2
        if self.moving_left:
            dx *= -1
        if self.moving_up:
            dy *= -1
        if self.phase:
            dx *= 3
            dy *= 3

        if not horizontal and not vertical:
            self.set_action("idle")
        elif self.moving_right:
            self.set_action("walk_right")
        elif self.moving_left:
            self.set_action("walk_left")
        elif self.moving_up:
            self.set_action("walk_up")
        elif self.moving_down:
            self.set_action("walk_down")

        return dx, dy
