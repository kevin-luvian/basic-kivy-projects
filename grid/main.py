from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import OptionProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.uix.behaviors import DragBehavior
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import Rectangle
from math import sqrt, pow, degrees, atan2
from random import randint, randrange

CLOCK_TIME = 1.0 / 60.0
NODE_SIZE = 41


class NodeBorder(Widget):
    pass


class Node(Widget):
    rgb = ListProperty([0.08, 0.08, 0.08])
    border = ObjectProperty(None)
    size = ListProperty([NODE_SIZE, NODE_SIZE])

    # def __init__(self, **kwargs):
    #     super(Node, self).__init__(**kwargs)

    def convert_to_wall(self):
        self.rgb = [91 / 255, 54 / 255, 33 / 255]

    def convert_to_start(self):
        self.rgb = [39 / 255, 196 / 255, 125 / 255]

    def convert_to_end(self):
        self.rgb = [239 / 255, 224 / 255, 19 / 255]


class Runner(Widget):
    start_node = None
    end_node = None
    nodes = []
    current_pos = (0, 0)
    len_x = 0
    len_y = 0
    pad_x = 0
    pad_y = 0

    def get_neighbours(self, node_pos):
        neighbours = []
        for y in [-1, 0, 1]:
            for x in [-1, 0, 1]:
                pos_y = node_pos + (self.len_x * y)
                pos = pos_y + x
                if 0 <= pos < len(self.nodes) and pos // self.len_x == pos_y // self.len_x:
                    neighbours.append(pos)
        return neighbours

    def build(self, *args):
        self.len_x = self.width // NODE_SIZE
        self.len_y = (self.height // NODE_SIZE) - 1
        self.pad_x = int((self.width % NODE_SIZE) // 2)
        self.pad_y = int((self.height % NODE_SIZE) // 2)
        self.current_pos = (self.pad_x, self.len_y * NODE_SIZE + self.pad_y)
        print("length_x: {0:d}, length_y: {1:d} pad_x: {2:d}, pad_y: {3:d}".format(self.len_x, self.len_y, self.pad_x,
                                                                                   self.pad_y))

    def draw(self, *args):
        print("i am updating")
        if self.current_pos[0] == self.len_x * NODE_SIZE + self.pad_x:
            pos_y = self.current_pos[1] - NODE_SIZE
            self.current_pos = (self.pad_x, pos_y)
            if pos_y < self.pad_y:
                return Clock.unschedule(self.draw)

        node = Node()
        node.pos = self.current_pos
        if randint(0, 100) <= 25:
            node.convert_to_wall()
        self.add_widget(node)
        self.nodes.append(node)
        self.current_pos = (self.current_pos[0] + NODE_SIZE, self.current_pos[1])

    def on_touch_down(self, touch):
        pos_x = touch.x - self.pad_x
        pos_y = touch.y - self.pad_y
        # print("cursor pos: {0:f},{1:f}".format(pos_x, pos_y))

        node_x = pos_x // NODE_SIZE
        node_y = abs((pos_y // NODE_SIZE) - self.len_y)
        # print("node pos: {0:f},{1:f}".format(node_x, node_y))

        node_loc = int(node_x + node_y * self.len_x)
        print("node location: {0:d}".format(node_loc))

        if self.start_node is None:
            self.start_node = self.nodes[node_loc]
            self.start_node.convert_to_start()
        elif self.start_node and self.end_node is None:
            self.end_node = self.nodes[node_loc]
            self.end_node.convert_to_end()
        else:
            print(*self.get_neighbours(node_loc), sep=", ")


class GridApp(App):
    def build(self):
        runner = Runner()
        Clock.schedule_once(runner.build, 0)
        Clock.schedule_interval(runner.draw, CLOCK_TIME)
        return runner


if __name__ == '__main__':
    GridApp().run()
