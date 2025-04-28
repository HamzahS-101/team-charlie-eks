import os

import pygame


class Frame:
    def __init__(self, image: pygame.Surface, duration: float) -> None:
        self.image = image
        self.duration = duration


class Animation(list[Frame]):
    def __init__(self, frames: list[Frame] = None, tags: list[str] = None) -> None:
        super().__init__(frames or [])
        self.tags = tags or []

    def is_last_frame(self, frame_index: int) -> bool:
        return frame_index == len(self) - 1


def collision_rect(rect: pygame.Rect, tiles: list[pygame.Rect]) -> list[pygame.Rect]:
    if len(tiles) == 0:
        return []

    hit_list = []

    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)

    return hit_list


def collision_mask(mask, other_mask):
    return pygame.sprite.collide_mask(mask, other_mask)


def blit_center(surface, other_surface, pos: tuple[int, int]) -> None:
    x = int(other_surface.get_width() / 2)
    y = int(other_surface.get_height() / 2)
    surface.blit(other_surface, (pos[0] - x, pos[1] - y))


def scale(image: pygame.Surface, image_size, scale: int) -> pygame.Surface:
    return pygame.transform.scale(image, (image_size[0] * scale, image_size[1] * scale))


def flip(
    image: pygame.Surface, flip_x: bool = False, flip_y: bool = False
) -> pygame.Surface:
    return pygame.transform.flip(image, flip_x, flip_y)


def load_image(file: str, colorkey: pygame.Color = "#FFFFFF") -> pygame.Surface:
    path = os.path.join("images", f"{file}.png")
    image = pygame.image.load(path).convert()

    if colorkey:
        image.set_colorkey(pygame.Color(colorkey))

    return image


def load_animation(
    path_or_images: str | list[pygame.Surface],
    frame_durations: list[float] = None,
    tags: list[str] = None,
    colorkey: pygame.Color = "#FFFFFF",
    start: int = None,
    end: int = None,
) -> Animation:
    animation_tags = tags or []
    start_frame = start if start is not None else 0
    end_frame = end if end is not None else -1  # inclusive

    frames = []

    if isinstance(path := path_or_images, str):
        for n, duration in enumerate(frame_durations):
            if n < start_frame or (end_frame != -1 and n > end_frame):
                continue
            animation_frame_id = f"{path}{n}"
            animation_image = load_image(animation_frame_id, colorkey)

            frames.append(Frame(animation_image, duration))

    elif isinstance(images := path, list):
        if end_frame == -1 or end_frame >= len(images):
            end_frame = len(images)

        if not frame_durations:
            frame_durations = [0.2] * len(images)

        for i, (image, duration) in enumerate(zip(images, frame_durations)):
            if i < start_frame or i >= end_frame:
                continue

            image.set_colorkey(colorkey)

            frames.append(Frame(image, duration))

    else:
        raise TypeError

    return Animation(frames, animation_tags)


def load_spritesheet(
    file: str, sprite_size: tuple[int, int], colorkey: pygame.Color = "#FFFFFF"
) -> list[pygame.Surface]:
    sprite_sheet = load_image(file, None)

    sheet_width = sprite_sheet.get_width()
    sprite_width, sprite_height = sprite_size
    num_sprites = sheet_width // sprite_width

    sprites = []
    for i in range(num_sprites):
        rect = pygame.Rect(i * sprite_width, 0, sprite_width, sprite_height)
        sprite = pygame.Surface(sprite_size)

        sprite.set_colorkey(pygame.Color(colorkey))

        sprite.blit(sprite_sheet, (0, 0), rect)
        sprites.append(sprite)

    return sprites


def button(screen, text, position, rect_size, size, text_color, background_color):
    font = pygame.font.SysFont("Arial", size)
    text_render = font.render(text, True, text_color)
    text_width, text_height = text_render.get_size()
    rect_width, rect_height = rect_size

    # Positioning the rectangle
    x, y = position
    rect_x = x - rect_width // 2
    rect_y = y - rect_height // 2

    # Positioning the text within the rectangle
    text_x = rect_x + (rect_width - text_width) // 2
    text_y = rect_y + (rect_height - text_height) // 2

    # Draw rectangle and text
    rect_tuple = (rect_x, rect_y, rect_width, rect_height)
    rect = pygame.draw.rect(screen, background_color, rect_tuple, border_radius=5)
    screen.blit(text_render, (text_x, text_y))

    return rect
