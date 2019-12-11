import sys
import time
import random
import pygame as pg

FPS = 60
SIZE = (480, 640)
SIZE_H = tuple(map(lambda x: int(x/2), SIZE))
TITLE = "TRAIN TRACKS"

NUM_TRACKS = 3


def main():
    pg.init()
    pg.display.set_caption(TITLE)
    screen = pg.display.set_mode(SIZE)
    clock = pg.time.Clock()

    train = Train(3)
    while True:
        # -- event loop
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()

        # -- draw
        screen.fill((100, 200, 100))
        draw_tracks(screen)
        train.draw(screen)
        pg.display.flip()

        # -- update
        delta_time = clock.tick(FPS) / 1000.0
        train.update(delta_time)


class Train:

    def __init__(self, track_number):
        random.seed(time.time())
        self.track_number = clamp(track_number, 1, NUM_TRACKS)
        self.move_dir = random.choice([-1, -1])
        self.speed = 250
        self.position = self.random_pos()
        self.num_containers = random.randrange(15, 50)
        self.cont_colors = self.random_colors(self.num_containers)

    def draw(self, surface):
        CHAIN_COLOR = (100, 100, 100, 255)

        cont_size = (80, 150)
        container_gap = 20
        for i in range(self.num_containers):
            px, py = self.position
            py += i * (-self.move_dir * (cont_size[1]+container_gap))
            pg.draw.rect(surface, self.cont_colors[i], self.rect_at((px, py), cont_size))
            pg.draw.rect(surface, CHAIN_COLOR, self.rect_at((px, py), cont_size), 3)

            if i < self.num_containers-1:
                py -= self.move_dir * (cont_size[1] + container_gap)//2
                joint_size = (5, container_gap)
                pg.draw.rect(surface, CHAIN_COLOR, self.rect_at((px, py), joint_size))

    def update(self, dt):
        px, py = self.position
        py += self.move_dir * self.speed * dt
        self.position = (px, py)

    def random_pos(self):
        track_width = SIZE[0] // NUM_TRACKS
        x_location = ((self.track_number-1) * track_width) + track_width//2
        return (x_location, 400)

    def random_colors(self, count):
        rr = random.randrange
        return [(rr(50, 150), 50, rr(20, 80) , 255) for _ in range(count)]

    def rect_at(self, center, size):
        sx, sy = size
        cx, cy = center
        return [cx-sx//2, cy-sy//2, sx, sy]


def draw_tracks(surface):
    TRACK_BACKGROUND = (81, 40, 16)
    RAIL_COLOR = (50, 40, 40)

    margins = 20
    track_width = (SIZE[0] // NUM_TRACKS) - (2*margins)
    track_height = SIZE[1]
    for i in range(NUM_TRACKS):
        loc_x = (i * (track_width+(2*margins))) + margins
        pg.draw.rect(surface, TRACK_BACKGROUND, [loc_x, 0, track_width, track_height])

        # -- draw rails
        rail_s = 10
        loc_x += track_width//2
        for r in [12, -12-rail_s]:
            pg.draw.rect(surface, RAIL_COLOR, [loc_x+r, 0, rail_s, track_height])


def clamp(value, _min, _max):
    return max(_min, min(_max, value))


if __name__ == '__main__':
    main()
