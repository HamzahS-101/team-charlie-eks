import random

import pygame
import settings as st
from entity import Entity
from level import Level
from pathfinder import bfs
from player import Player
from utils import load_spritesheet


class Bat(Entity):
    def __init__(self, rect):
        super().__init__(rect, "bat")

        self.load_animations(
            [
                {
                    "name": "idle",
                    "images": load_spritesheet(f"{self.path}idle", [16] * 2),
                    "tags": ["loop"],
                    "colorkey": (255, 0, 0),
                },
                {
                    "name": "fly_left",
                    "images": load_spritesheet(f"{self.path}fly_left", [16] * 2),
                    "tags": ["loop"],
                    "colorkey": (255, 0, 0),
                },
                {
                    "name": "fly_right",
                    "images": load_spritesheet(f"{self.path}fly_right", [16] * 2),
                    "tags": ["loop"],
                    "colorkey": (255, 0, 0),
                },
                {
                    "name": "fly_up",
                    "images": load_spritesheet(f"{self.path}fly_up", [16] * 2),
                    "tags": ["loop"],
                    "colorkey": (255, 0, 0),
                },
                {
                    "name": "fly_down",
                    "images": load_spritesheet(f"{self.path}fly_down", [16] * 2),
                    "tags": ["loop"],
                    "colorkey": (255, 0, 0),
                },
            ]
        )

        self.set_action("fly_right")
        self.collisions = {}
        self.player = None
        self.level = None

        self.seeking_player = True
        self.action_timer = 0

        self.previous_collisions = None
        self.current_direction = None

        self.next_step = None
        self.remainder_x = 0
        self.remainder_y = 0
        self.position_history = []  # List to keep track of past positions
        self.stuck_threshold = 10

    def update(self, dt: float, tiles, player: Player, level: Level):
        if not self.player or self.action_timer <= 0:
            self.player = player

        if not self.level or self.action_timer <= 0:
            self.level = level

        self.update_frame(dt)

        movement = self.move(dt)
        self.collisions = self.move_and_collide(movement, tiles)

        if self.collisions != self.previous_collisions:
            self.previous_collisions = self.collisions
            if self.collisions and not self.seeking_player:
                self.reset_position()
                self.random_direction()

        # # Detect if the bat is stuck and handle accordingly
        if self.is_stuck():
            self.reset_position()

        # Update the position history
        elif len(self.position_history) >= self.stuck_threshold:
            self.position_history.pop(0)
        elif self.rect.topleft not in self.position_history:
            self.position_history.append(self.rect.topleft)

        self.handle_ai_changes(dt)

    def move(self, dt: float):
        if self.seeking_player:
            return self.move_towards_player(dt)

        self.next_step = None
        self.remainder_x = 0
        self.remainder_y = 0
        self.level.from_box = None
        self.level.to_box = None
        self.level.to_boxes = []

        if self.current_action == "idle":
            return 0, 0

        return self.move_randomly(dt)

    def handle_ai_changes(self, dt):
        self.action_timer -= dt

        if self.action_timer > 0:
            return

        self.action_timer = 1
        has_set = False

        if random.random() < 0.20:  # do nothing
            self.set_action("idle")
            has_set = True
        elif random.random() < 0.33:  # seek player
            self.seeking_player = True
            self.move_towards_player(dt)
            self.set_action("fly_right")
            has_set = True

        if has_set:  # reset the position history
            self.current_direction = "fly_right"
        else:  # move randomly
            self.seeking_player = False
            self.move_randomly(dt)

    def random_direction(self):
        # Randomly choose a new direction that is not the current one
        directions = ["fly_left", "fly_right", "fly_up", "fly_down"]

        if self.current_direction:
            directions.remove(self.current_direction)

        if directions:
            self.current_direction = random.choice(directions)

        self.set_action(self.current_direction)

    def move_randomly(self, dt):
        speed = 75 * dt

        if self.current_direction is None:
            self.random_direction()

        if self.current_action == "fly_left":
            return -speed, 0
        if self.current_action == "fly_right":
            return speed, 0
        if self.current_action == "fly_up":
            return 0, -speed
        if self.current_action == "fly_down":
            return 0, speed

        return 0, 0

    def get_next_step(self):
        def div(x):
            return round(x / st.TILE_SIZE)

        start = (div(self.rect.y), div(self.rect.x))
        end = (div(self.player.rect.y), div(self.player.rect.x))

        grid = self.level.get_grid()
        path = bfs(grid, start, end)

        self.level.from_box = self.rect.topleft

        if not path or len(path) < 2:  # No path or already at destination
            print("No path")
            return 0, 0

        path = [(x, y) for y, x in path]  # flip x and y values

        next_step = path.pop(0)
        self.level.to_boxes = path
        return next_step

    def move_towards_player(self, dt: float):
        if self.next_step is None:
            self.next_step = self.get_next_step()

        if self.next_step is None:
            return 0, 0

        target_x = self.next_step[0] * st.TILE_SIZE
        target_y = self.next_step[1] * st.TILE_SIZE

        self.level.from_box = self.rect.topleft
        self.level.to_box = target_x, target_y

        dx, dy = 0, 0
        speed = 50 * dt
        tolerance = 1  # pixels

        difference_x = target_x - self.rect.x
        difference_y = target_y - self.rect.y
        tolerant_x = abs(difference_x) > tolerance
        tolerant_y = abs(difference_y) > tolerance

        # Apply the remainder only when close to the target tile
        if not tolerant_x:
            dx += self.remainder_x
            self.remainder_x = 0
        if not tolerant_y:
            dy += self.remainder_y
            self.remainder_y = 0

        # Move towards the next step, one axis at a time
        if tolerant_x:
            if target_x > self.rect.x:
                self.set_action("fly_right")
                dx = min(speed, difference_x)
            elif target_x < self.rect.x:
                self.set_action("fly_left")
                dx = -min(speed, -difference_x)

        elif tolerant_y:
            if target_y > self.rect.y:
                self.set_action("fly_down")
                dy = min(speed, difference_y)
            elif target_y < self.rect.y:
                self.set_action("fly_up")
                dy = -min(speed, -difference_y)

        dx, dy = round(dx, 2), round(dy, 2)

        # Check if the bat has reached the target tile
        if abs(difference_x) <= tolerance and abs(difference_y) <= tolerance:
            if len(self.level.to_boxes) > 0:
                self.get_next_step()
                self.next_step = self.level.to_boxes.pop(0)
                self.remainder_x = difference_x
                self.remainder_y = difference_y
            else:
                self.next_step = None
                self.remainder_x = 0  # Reset remainder
                self.remainder_y = 0
                return 0, 0

        return dx, dy

    def is_stuck(self):
        if len(self.position_history) < self.stuck_threshold:
            return False  # Not enough data to determine if stuck

        # Check for variability in positions
        unique_positions = set(self.position_history)
        if len(unique_positions) < len(self.position_history) / 2:
            return True

        # Check for repetitive patterns in the last few positions
        last_few_positions = self.position_history[-(self.stuck_threshold // 2) :]
        if last_few_positions.count(last_few_positions[0]) == len(last_few_positions):
            return True

        return False

    def reset_position(self):
        x, y = self.position_history.pop()

        x = round(x / st.TILE_SIZE) * st.TILE_SIZE
        y = round(y / st.TILE_SIZE) * st.TILE_SIZE

        # Reset the position to the last known good position
        self.rect.topleft = x, y
        self.x = x
        self.y = y
