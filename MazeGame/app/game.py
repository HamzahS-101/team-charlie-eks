import pygame
import settings as st
from bat import Bat
from entity import Entity
from level import Level
from player import Player


def update(dt: float, level, player, bats) -> None:
    tiles = level.walls
    player.update(dt, tiles)

    for bat in bats:
        bat.update(dt, tiles, player, level)


def main():
    # Initialize pygame
    width, height = st.WINDOW_WIDTH, st.WINDOW_HEIGHT
    screen = pygame.display.set_mode((width, height))
    game_surface = pygame.Surface((st.SURFACE_WIDTH, st.SURFACE_HEIGHT))
    clock = pygame.time.Clock()

    # Initialize game objects
    level = Level()
    start_pos = level.absoulte_pos(level.start_pos)
    end_rect = level.absoulte_pos(level.end_pos), (st.TILE_SIZE, st.TILE_SIZE)

    player = Player(pygame.Rect(start_pos, (16, 16)))
    bats: list[Bat] = []

    for _ in range(int(st.BAT_AMOUNT)):
        pos = level.absoulte_pos(level.get_random_pos())
        rect = pygame.Rect(pos, (16, 16))
        bat = Bat(rect)
        bats.append(bat)

    # Main game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                player.handle_keydown(event.key)
            if event.type == pygame.KEYUP:
                player.handle_keyup(event.key)

        game_surface.fill((0, 0, 0))

        # Check if player has reached the end
        if player.rect.colliderect(end_rect):
            st.HELP_AMOUNT -= 5
            st.BAT_AMOUNT += 0.5
            st.COIN_AMOUNT += 5
            return "You Win!"

        # if player collides with bat you lose
        for bat in bats:
            if player.rect.colliderect(bat):
                st.HELP_AMOUNT = 40
                st.BAT_AMOUNT = 3.0
                st.COIN_AMOUNT = 10
                return "You Lose!"

        # if player collides with coins del coin
        for coin in level.coins:
            if player.rect.colliderect(coin):
                level.coins.remove(coin)

        # Draw game here
        level.draw(game_surface)
        player.display(game_surface, (0, 0))
        for bat in bats:
            bat.display(game_surface, (0, 0))

        scaled_surface = pygame.transform.scale(game_surface, st.WINDOW_SIZE)
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

        # Update game objects here
        dt = clock.tick(60) / 1000.0
        update(dt, level, player, bats)

        # Set window name to framerate
        framerate = clock.get_fps()

        bat_ai = "seeking" if bats[0].seeking_player else "random"
        bat_ai = "idle" if bats[0].current_action == "idle" else bat_ai

        pygame.display.set_caption(f"Framerate: {framerate:.2f} | Bat AI {bat_ai}")


if __name__ == "__main__":
    main()
