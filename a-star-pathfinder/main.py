from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ListProperty, StringProperty
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from math import sqrt, pow
from random import randint
from kivy.core.window import Window
from operator import add

CLOCK_TIME = 1.0 / 60.0
NODES_SIZE = [80, 50]
WINDOW_SIZE = [1000, 600]


class LineDraw(Widget):
    path = ListProperty([0, 0])


class NodeBorder(Widget):
    pass


class Node(Widget):
    rgb = ListProperty([0.08, 0.08, 0.08])
    border = ObjectProperty(None)
    size = ListProperty([0, 0])
    label = StringProperty("")
    grid_pos = 0
    g_score = 0
    f_score = 0
    parent = None
    passable = True
    modifiable = True

    def __init__(self, size, grid_pos, pos, **kwargs):
        super(Node, self).__init__(**kwargs)
        self.size = size
        self.grid_pos = grid_pos
        self.pos = pos

    def convert_to_wall(self):
        self.rgb = [91 / 255, 54 / 255, 33 / 255]
        self.passable = False

    def convert_to_open(self):
        if self.modifiable:
            self.rgb = [106 / 255, 146 / 255, 204 / 255]
            # self.label = str(int(self.f_score))

    def convert_to_passed(self):
        if self.modifiable:
            self.rgb = [206 / 255, 36 / 255, 20 / 255]
            self.passable = False

    def convert_to_start(self):
        self.rgb = [39 / 255, 196 / 255, 125 / 255]
        self.modifiable = False

    def convert_to_end(self):
        self.rgb = [239 / 255, 224 / 255, 19 / 255]
        self.modifiable = False
        self.passable = True


class Runner(Widget):
    pad_y = 70
    start_node = None
    end_node = None
    nodes = []
    open_set = []

    def clear(self):
        self.nodes = []
        self.open_set = []
        self.start_node = None
        self.end_node = None
        self.clear_widgets()
        Clock.schedule_interval(self.build, 0)

    def get_neighbours(self, node):
        node_pos = self.get_node_pos(node.grid_pos)
        neighbours = []
        for y in [-1, 0, 1]:
            pos_y = (node_pos[1] + y) * NODES_SIZE[0]
            for x in [-1, 0, 1]:
                pos_x = node_pos[0] + x
                pos = pos_x + pos_y
                if 0 <= pos < len(self.nodes) and pos_y // NODES_SIZE[0] == pos // NODES_SIZE[0]:
                    target_node = self.nodes[pos]
                    if node_pos != pos and target_node.passable:
                        neighbours.append(target_node)
                        # if diagonal is block then remove
                        if y == -1 or y == 1 and x == -1 or x == 1:
                            check_pos_1 = self.nodes[pos - x].passable
                            check_pos_2 = self.nodes[pos + NODES_SIZE[0] * -y].passable
                            if not check_pos_1 and not check_pos_2:
                                neighbours.remove(target_node)
        return neighbours

    def get_node_pos(self, node_pos):
        pos_x = node_pos % NODES_SIZE[0]
        pos_y = node_pos // NODES_SIZE[0]
        return [pos_x, pos_y]

    def calculate_g_score(self, current_node, node):
        current_node_pos = self.get_node_pos(current_node.grid_pos)
        node_pos = self.get_node_pos(node.grid_pos)
        weight = 1
        if current_node_pos[0] != node_pos[0] and current_node_pos[1] != node_pos[1]:
            weight = sqrt(2 * pow(weight, 2))
        return current_node.g_score + weight

    def calculate_h_score(self, node):
        # node_pos = self.get_node_pos(node.grid_pos)
        # end_node_pos = self.get_node_pos(self.end_node.grid_pos)
        # dist_x = abs(node_pos[0] - end_node_pos[0])
        # dist_y = abs(node_pos[1] - end_node_pos[1])
        dist_x = abs(node.x - self.end_node.x)
        dist_y = abs(node.y - self.end_node.y)
        # manhattan_dist = dist_x + dist_y
        # euclidean_dist = sqrt(pow(dist_x, 2) + pow(dist_y, 2))
        diagonal_dist = max(dist_x, dist_y)
        return diagonal_dist

    def draw_line_path(self, node):
        center = [node.size[0] // 2, node.size[1] // 2]
        path = [list(map(add, [node.x, node.y], center))]
        parent_node = node
        while parent_node is not self.start_node:
            parent_node = parent_node.parent
            path.append(list(map(add, [parent_node.x, parent_node.y], center)))
        self.line_path.path = path

    def build(self, *args):
        print("building")
        size_x = WINDOW_SIZE[0] / NODES_SIZE[0]
        size_y = (WINDOW_SIZE[1] - self.pad_y) / NODES_SIZE[1]
        for i in range(NODES_SIZE[0] * NODES_SIZE[1]):
            pos_x = i % NODES_SIZE[0] * size_x
            pos_y = i // NODES_SIZE[0] * size_y
            node = Node([size_x, size_y], i, [pos_x, pos_y])

            # create wall node
            if randint(0, 100) <= 35:
                node.convert_to_wall()

            self.nodes.append(node)
            self.add_widget(node)

        self.line_path = LineDraw()
        self.add_widget(self.line_path)

        # create start node
        start_node = self.nodes[len(self.nodes) - NODES_SIZE[0]]
        start_node.convert_to_start()
        self.start_node = start_node
        self.open_set.append(start_node)

        # create end node
        end_node = self.nodes[NODES_SIZE[0] - 1]
        end_node.convert_to_end()
        self.end_node = end_node

    def update(self, *args):
        if len(self.open_set) == 0:
            print("No path found")
            Clock.unschedule(self.update)
            return

        current_node = None
        for node in self.open_set:
            if current_node is None or node.f_score < current_node.f_score:
                current_node = node

        if current_node is self.end_node:
            print("Finished")
            self.draw_line_path(self.end_node)
            Clock.unschedule(self.update)
            return

        current_node.convert_to_passed()
        self.open_set.remove(current_node)
        self.draw_line_path(current_node)
        neighbors = self.get_neighbours(current_node)
        for node in neighbors:
            temp_g_score = self.calculate_g_score(current_node, node)

            if node.g_score == 0 or temp_g_score < node.g_score:
                node.parent = current_node
                node.g_score = temp_g_score
                node.f_score = node.g_score + self.calculate_h_score(node)
                # print(node.f_score)
                if node not in self.open_set:
                    node.convert_to_open()
                    self.open_set.append(node)


class PathfinderApp(App):
    def build(self):
        runner = Runner()
        runner.build()
        Clock.schedule_interval(runner.update, CLOCK_TIME)
        return runner


if __name__ == '__main__':
    Window.size = WINDOW_SIZE
    PathfinderApp().run()
