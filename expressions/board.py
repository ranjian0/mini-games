import random
import pygame as pg
from collections import Counter


class Tile:
    TILE_SIZE = (100, 100)

    DEFAULT = 32
    FAIL = 33
    PASS = 34

    def __init__(self, pos, value):
        self.pos = pos
        self.value = value

        self.tile_yellow = pg.image.load("res/tile_yellow.png")
        self.tile_green = pg.image.load("res/tile_green.png")
        self.tile_hover = pg.image.load("res/tile_hover.png")
        self.tile_red = pg.image.load("res/tile_red.png")

        self.tile_rect = self.tile_yellow.get_rect(center=self.pos)
        self.text, self.text_rect = self.make_text()

        # Tile states
        self.hover = False
        self.tile_status = self.DEFAULT

    def set_fail(self):
        self.tile_status = self.FAIL

    def set_pass(self):
        self.tile_status = self.PASS

    def make_text(self):
        font = pg.font.SysFont("sans serif", 50)
        label = font.render(str(self.value), True, pg.Color("black"))
        label_rect = label.get_rect(center=self.pos)

        return label, label_rect

    def draw(self, surface):
        tile = {
            self.DEFAULT: self.tile_yellow,
            self.FAIL: self.tile_red,
            self.PASS: self.tile_green,
        }.get(self.tile_status)

        surface.blit(tile, tile.get_rect(center=self.pos))
        if self.hover:
            surface.blit(self.tile_hover, self.tile_hover.get_rect(center=self.pos))

        surface.blit(self.text, self.text_rect)

    def update(self):
        pos = pg.mouse.get_pos()
        if self.tile_rect.collidepoint(pos):
            self.hover = True
        else:
            self.hover = False


class Target(object):
    def __init__(self, pos):
        self.pos = pos
        self.value = self.generate_expression()
        self.text, self.text_rect = self.setup_font()

    def setup_font(self):
        font = pg.font.SysFont("timesnewroman", 25)
        label = font.render(str(self.value), True, pg.Color("white"))
        label_rect = label.get_rect(center=self.pos)

        return label, label_rect

    def draw(self, surface):
        surface.blit(self.text, self.text_rect)

    def reset(self):
        self.value = self.generate_expression()
        self.text, self.text_rect = self.setup_font()

    def generate_expression(self):
        fnum, snum = [random.randint(11, 99) for _ in range(2)]

        if fnum < snum:
            fnum, snum = snum, fnum
        operation = random.choice(["+", "-", "*"])

        text = "{0} {1} {2}".format(fnum, operation, snum)
        self.result = eval(text)

        return text


class Board(object):
    TILE_SIZE = (100, 100)

    def __init__(self, screen_rect):
        self.screen_rect = screen_rect
        self.tiles = []
        self.target = Target(screen_rect.center)

        self.make_board()
        self.board_score = 0

    def make_board(self):
        self.target.reset()
        positions = self.tile_positions()
        values = self.tile_values()

        for pos in positions:
            rand_value = values[positions.index(pos)]
            t = Tile(pos, rand_value)
            self.tiles.append(t)

    def tile_positions(self):
        # Create positions for top, left, bottom and right part of screen
        positions = [
            (self.screen_rect.size[0] * 0.5, self.screen_rect.size[1] * 0.25),  # TOP
            (self.screen_rect.size[0] * 0.75, self.screen_rect.size[1] * 0.5),  # RIGHT
            (self.screen_rect.size[0] * 0.5, self.screen_rect.size[1] * 0.75),  # BOTTOM
            (self.screen_rect.size[0] * 0.25, self.screen_rect.size[1] * 0.5),
        ]  # LEFT

        return positions

    def tile_values(self):
        res = self.target.result
        values = [0, 0, 0, 0]
        values[random.randint(0, len(values) - 1)] = round(res, 2)

        epsilon = int(res + (res / 2))
        for idx, v in enumerate(values):
            if v == 0:
                rvalue = random.randint(res, epsilon)
                values[idx] = rvalue

        def remove_duplicates(vals):
            duplicate, count = Counter(vals).most_common(1)[0]
            for i in range(count - 1):
                r = random.randint(0, 10)
                vals[vals.index(duplicate)] += r

            if len(values) > len(set(values)):
                return remove_duplicates(values)
            return values

        # Remove duplicates
        if len(values) > len(set(values)):
            values = remove_duplicates(values)
        return values

    def reset(self):
        self.tiles.clear()
        self.make_board()

    def on_mouse(self, pos, t):
        for tile in self.tiles:
            if tile.tile_rect.collidepoint(*pos):
                if tile.value == self.target.result:
                    tile.set_pass()
                    self.board_score += 1
                    t.add_timer(25)
                    self.reset()
                else:
                    tile.set_fail()
                    t.subtract_timer(10)

    def draw(self, surface):
        self.target.draw(surface)
        for tile in self.tiles:
            tile.draw(surface)

    def update(self):
        for tile in self.tiles:
            tile.update()
