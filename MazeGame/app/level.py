import os
import random

import pygame
import settings as st
from utils import load_image, load_spritesheet


class Level:
    def __init__(self):
        path = f"tilesets{os.sep}"
        self.background_tiles = load_spritesheet(f"{path}background", [16] * 2)
        self.left_right_tiles = load_spritesheet(f"{path}left_right", [16] * 2)
        self.up_down_tiles = load_spritesheet(f"{path}up_down", [16] * 2)
        self.tunnels_tiles = load_spritesheet(f"{path}tunnels", [16] * 2)

        self.coin_image = load_image(f"{path}coin")
        entrance_image = load_image(f"{path}entrance")
        exit_image = load_image(f"{path}exit")

        maze_object = self.generate_maze(st.SIZE_X, st.SIZE_Y)
        self.maze, self.start_pos, self.end_pos = maze_object

        self.tile_selections = {}
        for coord, col in self.maze.items():
            if col in [0, 3]:  # Air or Coin
                tile = random.choice(self.background_tiles).copy()
                self.tile_selections[coord] = tile
            elif col == 1:  # Wall
                tile = self.get_wall_tile(coord).copy()
                self.tile_selections[coord] = tile
            if col == 2:  # Tunnel
                tile = random.choice(self.background_tiles).copy()
                tunnel = random.choice(self.tunnels_tiles).copy()
                tile.blit(tunnel, (0, 0))
                self.tile_selections[coord] = tile

        # blit the entrance to the start position
        new_entrance = self.tile_selections[self.start_pos].copy()
        new_entrance.blit(entrance_image, (0, 0))
        self.tile_selections[self.start_pos] = new_entrance

        # blit the exit to the end position
        new_exit = self.tile_selections[self.end_pos].copy()
        new_exit.blit(exit_image, (0, 0))
        self.tile_selections[self.end_pos] = new_exit

        self.walls = []
        self.tunnels = []
        self.coins = []

        self.frame = 0

        self.from_box = None  # TODO
        self.to_box = None
        self.to_boxes = []

    def absoulte_pos(self, pos):
        if isinstance(pos, str):
            pos = pos.split(";")
            x, y = int(pos[0]), int(pos[1])
        elif isinstance(pos, tuple):
            x, y = pos

        return x * st.TILE_SIZE, y * st.TILE_SIZE

    def draw(self, screen):
        size_2d = (st.TILE_SIZE, st.TILE_SIZE)

        if not self.walls:
            for coord, col in self.maze.items():
                if col == 0:
                    continue

                rect = pygame.Rect(self.absoulte_pos(coord), size_2d)

                if col == 1:
                    self.walls.append(rect)
                elif col == 2:
                    self.tunnels.append(rect)
                elif col == 3:
                    self.coins.append(rect)

            # add boundary walls
            for x in range(st.SIZE_X):
                self.walls.extend(
                    [
                        pygame.Rect(self.absoulte_pos((x, -1)), size_2d),  # U
                        pygame.Rect(self.absoulte_pos((-1, x)), size_2d),  # L
                        pygame.Rect(self.absoulte_pos((st.SIZE_X, x)), size_2d),  # R
                        pygame.Rect(self.absoulte_pos((x, st.SIZE_Y)), size_2d),  # D
                    ]
                )

        topleft_coins = [coin.topleft for coin in self.coins]

        # Draw tiles based on the tile type
        for coord, col in self.maze.items():
            x, y = self.absoulte_pos(coord)
            tile = self.tile_selections.get(coord)
            screen.blit(tile, (x, y))

            if col == 3 and (x, y) in topleft_coins:  # Coin
                screen.blit(self.coin_image, (x, y))

        # Additional drawing logic (such as drawing start/end positions, test boxes, etc.)
        self.frame += 1
        if self.frame == 30:
            self.frame = 0

        # Draw test boxes
        # if self.from_box:
        #     pygame.draw.rect(
        #         screen, (12, 100, 0), pygame.Rect((self.from_box), size_2d)
        #     )

        # for boxes in self.to_boxes:
        #     bx, by = boxes
        #     bx *= st.TILE_SIZE
        #     by *= st.TILE_SIZE

        #     # Create a Surface with the SRCALPHA flag
        #     transparent_surface = pygame.Surface(size_2d, pygame.SRCALPHA)
        #     rgba_color = (255, 100, 100, 100)  # Change the last value for transparency
        #     pygame.draw.rect(
        #         transparent_surface, rgba_color, transparent_surface.get_rect()
        #     )
        #     screen.blit(transparent_surface, (bx, by))

        # if self.to_box:
        #     pygame.draw.rect(screen, (255, 0, 100), pygame.Rect((self.to_box), size_2d))

    def generate_maze(self, width, height):
        # Initialize the maze dict with 1's (walls)
        maze = {}
        for x in range(width):
            for y in range(height):
                maze[f"{x};{y}"] = 1

        # Define function to carve paths
        def carve(x, y):
            # Define the 4 directions (up, right, down, left)
            dir = [(0, -1), (1, 0), (0, 1), (-1, 0)]
            random.shuffle(dir)  # Randomize the directions

            # Carve paths in the random directions
            for dx, dy in dir:
                nx, ny = x + dx * 2, y + dy * 2
                if 0 <= nx < width and 0 <= ny < height and maze.get(f"{nx};{ny}") == 1:
                    maze[f"{nx};{ny}"] = 0
                    maze[f"{x + dx};{y + dy}"] = 0
                    carve(nx, ny)

        # Random starting position
        start_x, start_y = random.randint(0, width - 1), random.randint(0, height - 1)
        maze[f"{start_x};{start_y}"] = 0
        carve(start_x, start_y)

        # Determine the ending position far from the start
        end_x, end_y = start_x, start_y
        while (abs(start_x - end_x) + abs(start_y - end_y)) < max(
            width, height
        ) / 2 or maze.get(f"{end_x};{end_y}") == 1:
            end_x, end_y = random.randint(0, width - 1), random.randint(0, height - 1)

        start_pos = f"{start_x};{start_y}"
        end_pos = f"{end_x};{end_y}"

        # Whitelist spots to make the maze easier
        maze = self.add_tunnels(maze, width, height)
        maze = self.add_coins(maze, width, height)

        return maze, start_pos, end_pos

    def add_tunnels(self, maze, width, height):
        tunnels = 0
        while tunnels < st.HELP_AMOUNT:
            coord = random.randint(0, width - 1), random.randint(0, height - 1)
            random_x, random_y = coord

            # Check if the selected cell is a wall
            if maze.get(f"{random_x};{random_y}") != 1:
                continue

            # Check surrounding cells
            left = maze.get(f"{random_x - 1};{random_y}", -1)  # Left cell
            right = maze.get(f"{random_x + 1};{random_y}", -1)  # Right cell
            up = maze.get(f"{random_x};{random_y - 1}", -1)  # Upper cell
            down = maze.get(f"{random_x};{random_y + 1}", -1)  # Lower cell

            # Check for proper tunnel conditions
            horizontal_cond = left == 1 and right == 1 and up == 0 and down == 0
            vertical_cond = up == 1 and down == 1 and left == 0 and right == 0

            if horizontal_cond or vertical_cond:
                maze[f"{random_x};{random_y}"] = 2
                tunnels += 1

        return maze

    def add_coins(self, maze, width, height):
        coins = 0
        while coins < st.COIN_AMOUNT:
            coord = random.randint(0, width - 1), random.randint(0, height - 1)
            random_x, random_y = coord

            # Check if the selected cell is an air spot
            if maze.get(f"{random_x};{random_y}") == 0:
                maze[f"{random_x};{random_y}"] = 3  # 3 represents a coin
                coins += 1

        return maze

    def get_random_pos(self):
        # can only get random air tiles
        while True:
            pos = random.choice(list(self.maze.keys()))
            item = self.maze.get(pos)

            if item == 0:
                return pos

    def get_grid(self):
        grid = []
        for y in range(st.SIZE_Y):
            row = []
            for x in range(st.SIZE_X):
                cell = self.maze.get(f"{x};{y}")
                row.append(1 if cell == 1 else 0)  # 0 for passable, 1 for walls
            grid.append(row)

        # print(grid)
        return grid

    def get_wall_tile(self, coord):
        # Check neighboring tiles to determine the correct wall tile
        left = self.maze.get(f"{int(coord.split(';')[0]) - 1};{coord.split(';')[1]}")
        right = self.maze.get(f"{int(coord.split(';')[0]) + 1};{coord.split(';')[1]}")
        up = self.maze.get(f"{coord.split(';')[0]};{int(coord.split(';')[1]) - 1}")
        down = self.maze.get(f"{coord.split(';')[0]};{int(coord.split(';')[1]) + 1}")

        if down == 0:
            return random.choice(self.up_down_tiles)
        if left == 0 and right == 0:
            return random.choice(self.left_right_tiles)

        return random.choice(self.left_right_tiles)
