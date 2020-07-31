from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from random import randint
from operator import add

GRID_SIZE = 65


def move_set(unit_name, unit_pos, board):
    moveset = []
    attackset = []

    # check rook and queen
    if unit_name in ["bR1", "bR2", "wR1", "wR2", "bQ", "wQ"]:
        for direction in [[1, 0], [-1, 0], [0, 1], [0, -1]]:
            pos_x = unit_pos[0]
            pos_y = unit_pos[1]
            while True:
                pos_x += direction[0]
                pos_y += direction[1]
                if 0 <= pos_x < len(board[0]) and 0 <= pos_y < len(board):
                    board_name = board[pos_y][pos_x]
                    if board_name == "":
                        moveset.append([pos_x, pos_y])
                    else:
                        attackset.append([pos_x, pos_y])
                        break
                else:
                    break

    # check knight
    if unit_name in ["bN1", "bN2", "wN1", "wN2"]:
        for mult in [[2, 1], [1, 2]]:
            for x in [-1, 1]:
                pos_x = mult[0] * x + unit_pos[0]
                if pos_x < 0 or pos_x >= len(board[0]):
                    continue
                for y in [-1, 1]:
                    pos_y = mult[1] * y + unit_pos[1]
                    if pos_y < 0 or pos_y >= len(board):
                        continue
                    board_name = board[pos_y][pos_x]
                    if board_name == "":
                        moveset.append([pos_x, pos_y])

    # check bishop and queen
    if unit_name in ["bB1", "bB2", "wB1", "wB2", "bQ", "wQ"]:
        for mult in [[1, 1], [-1, 1], [1, -1], [-1, -1]]:
            i = 0
            while True:
                i += 1
                pos_x = unit_pos[0] + i * mult[0]
                pos_y = unit_pos[1] + i * mult[1]
                if 0 <= pos_x < len(board[0]) and 0 <= pos_y < len(board):
                    board_name = board[pos_y][pos_x]
                    if board_name == "":
                        moveset.append([pos_x, pos_y])
                    else:
                        break
                else:
                    break

    # check king
    if unit_name in ["bK", "wK"]:
        for y in range(-1, 2):
            pos_y = unit_pos[1] + y
            if pos_y < 0 or pos_y >= len(board):
                continue
            for x in range(-1, 2):
                pos_x = unit_pos[0] + x
                if pos_x < 0 or pos_x >= len(board[1]):
                    continue
                board_name = board[pos_y][pos_x]
                if board_name == "":
                    moveset.append([pos_x, pos_y])
                elif unit_pos == [pos_x, pos_y]:
                    continue
                else:
                    continue

    # check white pawn
    if unit_name in ["wP1", "wP2", "wP3", "wP4", "wP5", "wP6", "wP7", "wP8"]:
        y = 1
        pos_y = unit_pos[1]
        while True:
            pos_y += y
            board_name = board[pos_y][unit_pos[0]]
            if board_name == "":
                moveset.append([unit_pos[0], pos_y])
            else:
                break
            if unit_pos[1] == 1:
                if pos_y > 2:
                    break

    # check black pawn
    if unit_name in ["bP1", "bP2", "bP3", "bP4", "bP5", "bP6", "bP7", "bP8"]:
        y = -1
        pos_y = unit_pos[1]
        while True:
            pos_y += y
            board_name = board[pos_y][unit_pos[0]]
            if board_name == "":
                moveset.append([unit_pos[0], pos_y])
            else:
                break
            if unit_pos[1] == 6:
                if pos_y < 5:
                    break
    return moveset, attackset


class Unit(Widget):
    size = ListProperty([GRID_SIZE - 10, GRID_SIZE - 10])
    pos = ListProperty([0, 0])
    rgb = ListProperty([0, 0, 0])
    name = StringProperty("")

    def __init__(self, name, pos, rgb, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.pos = pos
        self.rgb = rgb


class Grid(Widget):
    size = ListProperty([GRID_SIZE, GRID_SIZE])
    pos = ListProperty([0, 0])
    rgb = ListProperty([1., 1., 1.])
    default_rgb = []

    def __init__(self, pos, rgb, **kwargs):
        super().__init__(**kwargs)
        self.pos = pos
        self.rgb = rgb
        self.default_rgb = rgb

    def reset_rgb(self):
        self.rgb = self.default_rgb

    def active(self):
        self.rgb = [36 / 255, 204 / 255, 72 / 255]

    def danger(self):
        self.rgb = [242 / 255, 249 / 255, 14 / 255]


class Runner(Widget):
    pad = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.board_pos = [
            ["wR1", "wN1", "wB1", "", "", "wB2", "wN2", "wR2"],
            ["wP1", "wP2", "wP3", "wP4", "wP5", "wP6", "wP7", "wP8"],
            ["", "", "wQ", "", "", "", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["", "bR1", "", "wK", "", "bQ", "", ""],
            ["", "", "", "", "", "", "", ""],
            ["bP1", "bP2", "bP3", "bP4", "bP5", "bP6", "bP7", "bP8"],
            ["", "bN1", "bB1", "bK", "", "bB2", "bN2", "bR2"],
        ]
        self.board = []
        self.units = {}

    def build(self, *args):
        self.pad = [(self.width - GRID_SIZE * 8) // 2, (self.height - GRID_SIZE * 8) // 2]
        for y in range(8):
            column = []
            for x in range(8):
                color = [1., 1., 1.] if (x + y) % 2 == 1 else [0.2, 0.2, 0.2]
                grid_pos = [GRID_SIZE * x + self.pad[0], GRID_SIZE * y + self.pad[1]]
                grid = Grid(grid_pos, color)
                column.append(grid)
                self.add_widget(grid)
                unit_name = self.board_pos[y][x]
                if unit_name != "":
                    unit = Unit(unit_name, [grid_pos[0] + 5, grid_pos[1] + 5], [1., 0, 0])
                    self.add_widget(unit)
                    self.units[unit_name] = unit
            self.board.append(column)

    def update(self, *args):
        pass

    def reset_grid_color(self):
        for column in self.board:
            for grid in column:
                grid.reset_rgb()

    def on_touch_down(self, touch):
        touch_grid_pos = [int((touch.pos[0] - self.pad[0]) // GRID_SIZE),
                          int((touch.pos[1] - self.pad[1]) // GRID_SIZE)]
        if 0 <= touch_grid_pos[1] < len(self.board) and 0 <= touch_grid_pos[0] < len(self.board[0]):
            self.reset_grid_color()
            # self.board[touch_grid_pos[1]][touch_grid_pos[0]].rgb = [1., 1., 0]
            unit_name = self.board_pos[touch_grid_pos[1]][touch_grid_pos[0]]
            if unit_name != "":
                moveset, attackset = move_set(unit_name, touch_grid_pos, self.board_pos)
                for move in moveset:
                    # print("move pos", move_pos)
                    self.board[move[1]][move[0]].active()
                for attack in attackset:
                    self.board[attack[1]][attack[0]].danger()


class ChessApp(App):
    def build(self):
        runner = Runner()
        Clock.schedule_once(runner.build, 0)
        Clock.schedule_interval(runner.update, 1.0 / 15.0)
        return runner


if __name__ == '__main__':
    ChessApp().run()
