import sys
import time
import random
import pygame as pg

from pygame import gfxdraw
from dataclasses import dataclass

SIZE = (480, 640)
SIZE_H = tuple(map(lambda x: int(x/2), SIZE))
TITLE = "Cancer Cell"

EVT_SHRINKED = pg.USEREVENT + 1
SHRINKED = pg.event.Event(EVT_SHRINKED)


class Game:

    def __init__(self):
        self.screen = pg.display.set_mode(SIZE)
        self.clock = pg.time.Clock()

        self.flick_item = FlickItem()
        self.flick_targets = FlickTargets(self.flick_item, [])

    def run(self):
        delta_time = 0
        show_game_over = False
        while True:
            # --EVENTS
            for ev in pg.event.get():
                if ev.type == pg.QUIT:
                    sys.exit()

                if ev.type == pg.VIDEORESIZE:
                    self.screen = pg.display.set_mode(ev.size, pg.RESIZABLE)

                if ev.type == pg.KEYDOWN:
                    if ev.key == pg.K_ESCAPE:
                        sys.exit()

                    if show_game_over and ev.key == pg.K_SPACE:
                        show_game_over = False

                if ev.type == EVT_SHRINKED:
                    show_game_over = True

                if not show_game_over:
                    self.flick_item.event(ev)

            # --DRAW
            self.screen.fill((100, 100, 100))
            if show_game_over:
                draw_game_over(self.screen)
            else:
                self.flick_targets.draw(self.screen)
                self.flick_item.draw(self.screen)
            pg.display.flip()

            # --UPDATE
            delta_time = self.clock.tick(60) / 1000
            if not show_game_over:
                self.flick_item.update(delta_time)
                self.flick_targets.update(delta_time)


@dataclass
class FlickItem:
    size: float = 50
    speed: float = 1000.0
    color: tuple = (255, 255, 255)
    position: tuple = SIZE_H
    flick_direction: tuple = (0, 0)

    def reset(self):
        self.flick_direction = (0, 0)
        self.position = SIZE_H

    def update(self, delta_time):
        px, py = self.position
        dx, dy = self.flick_direction
        px += dx * self.speed * delta_time
        py += dy * self.speed * delta_time
        self.position = (int(px), int(py))

    def draw(self, surface):
        gfxdraw.aacircle(surface, *self.position, self.size//2, self.color)
        gfxdraw.filled_circle(surface, *self.position, self.size//2, self.color)

    def event(self, ev):
        if ev.type == pg.KEYDOWN:
            key_map = {
                pg.K_UP :   (0, -1),
                pg.K_DOWN : (0,  1),
                pg.K_LEFT : (-1,  0),
                pg.K_RIGHT: (1, 0)
            }
            direction = key_map.get(ev.key, None)
            if direction:
                self.flick_direction = direction


@dataclass
class FlickTargets:
    flick_item: FlickItem
    colors: list
    size: float = 50
    wait_time: float = .3
    current_time: float = 0
    shrink_speed: float = 15

    def __post_init__(self):
        self.set_colors()

    def set_colors(self):
        random.seed(time.time())
        self.colors = [
            (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            for _ in range(4)
        ]
        self.flick_item.color = random.choice(self.colors)
        return self.colors

    def draw(self, surface):
        WIDTH, HEIGHT = SIZE
        SIZE_H_X, SIZE_H_Y = SIZE_H

        ellipse_rects = [
            # cx cy rx ry
            [WIDTH//2, 0, WIDTH//2, self.size],          # Top
            [0, HEIGHT//2, self.size, HEIGHT//2],        # Left
            [WIDTH//2, HEIGHT, WIDTH//2, self.size],     # Bottom
            [WIDTH, HEIGHT//2, self.size, HEIGHT//2],    # Right
        ]

        for col, rect in zip(self.colors, ellipse_rects):
            ellipse = tuple(map(int, rect))
            if any(val < 0 for val in ellipse):
                continue
            gfxdraw.aaellipse(surface, *ellipse, col)
            gfxdraw.filled_ellipse(surface, *ellipse, col)

    def update(self, delta_time):
        self.size += delta_time * self.shrink_speed
        if self.size <= 1.0:
            self.size = 50
            self.set_colors()
            pg.event.post(SHRINKED)

        direction = self.flick_item.flick_direction
        if sum(direction) == 0:
            return

        direction_to_color_index = {
            (-1, 0) : 1,    # Left
            (1, 0): 3,      # Right
            (0, 1): 2,      # Top
            (0, -1): 0      # Bottom
        }

        target_color = self.colors[direction_to_color_index[direction]]
        if target_color == self.flick_item.color:
            self.current_time += delta_time
            if self.current_time >= self.wait_time:
                self.flick_item.reset()
                self.set_colors()
                self.current_time = 0
                self.size -= 20

        else:
            self.flick_item.reset()
            self.set_colors()
            self.size += 20


def draw_game_over(surface):
    font_name = pg.font.match_font("arial")

    # -- Draw Game Over Text
    font = pg.font.Font(font_name, 40)
    font.set_bold(True)

    tsurface = font.render("GAME OVER", True, pg.Color("red"))
    text_rect = tsurface.get_rect()
    text_rect.center = (SIZE[0] // 2, 100)
    surface.blit(tsurface, text_rect)

    # # -- Draw score text
    # font = pg.font.Font(font_name, 20)
    # font.set_bold(True)

    # tsurface = font.render("Your Score " + str(score), True, pg.Color("white"))
    # text_rect = tsurface.get_rect()
    # text_rect.center = (SIZE[0] // 2, 200)
    # surface.blit(tsurface, text_rect)

    # -- Draw instructions
    font = pg.font.Font(font_name, 12)
    font.set_bold(True)
    font.set_italic(True)

    tsurface = font.render(
        "Press Escape to QUIT, Space to RESTART", True, pg.Color("white")
    )
    text_rect = tsurface.get_rect()
    text_rect.center = (SIZE[0] // 2, SIZE[1] - 20)
    surface.blit(tsurface, text_rect)


def main():
    pg.init()
    pg.display.set_caption(TITLE)
    game = Game()
    game.run()
    return 0


if __name__ == '__main__':
    sys.exit(main())
