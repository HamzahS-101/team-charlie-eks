import os

import pygame

from utils import Animation, blit_center, collision_rect, flip, load_animation


class Entity:
    animation: dict[str, Animation] = {}

    def __init__(self, rect, entity_type) -> None:
        self.type = entity_type
        self.path = os.path.join(self.type) + os.sep

        # physical stuff
        self.rect: pygame.Rect = rect
        self.x = self.rect.x
        self.y = self.rect.y
        self.width = self.rect.width
        self.height = self.rect.height
        self.offset = [0, 0]

        # image stuff
        self._image: pygame.Surface = None
        self.flip = False

        # animation stuff
        self.current_frame = 0
        self.frame_time = 0
        self.frame_duration = 0
        self.current_action = ""
        self.phase = False

    def image(self):
        key = f"{self.type};{self.current_action}"
        animation = self.animation.get(key, False)

        if animation and 0 <= self.current_frame < len(animation):
            self._image = animation[self.current_frame].image

        return self._image

    def animation_key(self):
        return f"{self.type};{self.current_action}"

    def load_animations(self, animations: list[dict[str]]) -> None:
        for data in animations:
            name = data["name"]
            durations: list[float] = data.get("durations", [])
            tags: list[str] = data.get("tags", [])
            colorkey = data.get("colorkey", "#FFFFFF")
            start = data.get("start", None)
            end = data.get("end", None)

            if images := data.get("images", []):
                path_or_images = images
            else:
                path_or_images = os.path.join(self.type, name)

            args = path_or_images, durations, tags, colorkey, start, end
            self.animation[f"{self.type};{name}"] = load_animation(*args)

    def set_action(self, new_action: str) -> None:
        if self.current_action == new_action:
            return

        # print(f"Set action for {self.type} to {new_action}")

        self.current_action = new_action
        self.current_frame = 0
        self.frame_time = 0

        animation = self.animation[self.animation_key()]
        self.frame_duration = animation[self.current_frame].duration

    def update_frame(self, dt: float, direction: int = 1) -> None:
        self.frame_time += dt

        if self.frame_time >= self.frame_duration:
            self.frame_time = 0
            frames = self.animation[self.animation_key()]

            dire = 1 if direction >= 0 else -1
            next_frame = (self.current_frame + dire) % len(frames)

            self.frame_duration = frames[next_frame].duration

            end_forward = direction == 1 and next_frame == 0
            end_backward = direction == -1 and next_frame == len(frames) - 1

            if "loop" in frames.tags or not (end_forward or end_backward):
                self.current_frame = next_frame
                return

            self.current_frame = len(frames) - 1 if end_forward else 0

    def prepare_image(self) -> tuple[pygame.Surface, float, float]:
        if self.animation:
            pre_image = self.animation[self.animation_key()][self.current_frame].image

        else:
            pre_image = self.image() or None

        if not pre_image:
            return None

        image = flip(pre_image, self.flip).copy()
        center_x = image.get_width() / 2
        center_y = image.get_height() / 2

        return image, center_x, center_y

    def display(
        self, surface: pygame.Surface, viewport_origin: tuple[int, int]
    ) -> None:
        data = self.prepare_image()

        if data is None or len(data) != 3:
            raise ValueError("No image to display")

        flip_offset = self.rect.width if self.flip else 0

        image, center_x, center_y = data
        pos_x = int(self.x) - viewport_origin[0] + self.offset[0] + center_x
        pos_y = int(self.y) - viewport_origin[1] + self.offset[1] + center_y

        blit_center(surface, image, (pos_x - flip_offset, pos_y))

    def move_and_collide(
        self, movement: tuple[int, int], all_tiles: list[pygame.Rect]
    ) -> dict[str, bool]:
        collision_types = {"left": False, "top": False, "right": False, "bottom": False}
        tiles = all_tiles.copy()

        self.x += movement[0]
        self.rect.x = int(self.x)

        block_hit_list: list[pygame.Rect] = collision_rect(self.rect, tiles)
        for block in block_hit_list:
            if self.phase:
                continue

            if movement[0] > 0:
                self.rect.right = block.left
                collision_types["right"] = True
            elif movement[0] < 0:
                self.rect.left = block.right
                collision_types["left"] = True

            self.x = self.rect.x

        self.y += movement[1]
        self.rect.y = int(self.y)

        block_hit_list: list[pygame.Rect] = collision_rect(self.rect, tiles)
        for block in block_hit_list:
            if self.phase:
                continue

            if movement[1] > 0:
                self.rect.bottom = block.top
                collision_types["bottom"] = True
            elif movement[1] < 0:
                self.rect.top = block.bottom
                collision_types["top"] = True

            self.y = self.rect.y

        return collision_types
