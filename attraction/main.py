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

GRAVITY = 3


class Attractor(Widget):
    pos = ListProperty([0, 0])
    repulsion_radius = 30

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            self.pos = (touch.x - self.center_x, touch.y - self.center_y)


class Rock(Widget):
    pos = ListProperty([0, 0])
    acceleration = Vector(0, 0)
    velocity = Vector(0, 0)
    life_count = 0
    life_line = 0

    def create_random_pos(self, max_x, max_y):
        rand_bool = bool(randint(0, 1))
        rand_width = 0 if rand_bool else randint(0, max_x)
        rand_height = 0 if not rand_bool else randint(0, max_y)
        return [rand_width, rand_height]

    def get_angle(self, point):
        len_x = point[0] - self.pos[0]
        len_y = point[1] - self.pos[1]
        return degrees(atan2(len_y, len_x))

    def accelerate_once(self):
        self.velocity = self.velocity + self.acceleration
        self.acceleration = self.acceleration * 0

    def accelerate_to(self, attractor):
        center_target = attractor.pos + attractor.center
        center_pos = self.pos + self.center
        force = Vector(center_target[0] - center_pos[0],
                       center_target[1] - center_pos[1])
        if force.length() <= attractor.repulsion_radius:
            force *= -1

        gravity_strength = GRAVITY / pow(force.length(), 2)
        force *= max(min(10, gravity_strength), 0)
        self.acceleration = self.acceleration + force

    def reset(self):
        self.life_count = 0
        self.acceleration *= 0
        self.velocity *= 0
        self.pos = self.create_random_pos(self.parent.width, self.parent.height)

    def move(self):
        if self.life_count > self.life_line:
            self.reset()
        else:
            self.accelerate_once()
            self.pos = Vector(self.pos) + self.velocity
            self.life_count += 1


class Runner(Widget):
    rocks = []
    attractors = []

    def create_random_pos(self, max_x, max_y):
        rand_bool = bool(randint(0, 1))
        rand_width = 0 if rand_bool else randint(0, max_x)
        rand_height = 0 if not rand_bool else randint(0, max_y)
        return [rand_width, rand_height]

    def on_start(self):
        print("im starting")

    def build(self, *args):
        for i in range(100):
            rock = Rock()
            rock.pos = [randint(self.center_x - 30, self.center_x + 30),
                        randint(self.center_y - 30, self.center_y + 30)]
            self.add_widget(rock)
            self.rocks.append(rock)

    def update(self, *args):
        if len(self.rocks) < 100:
            rock = Rock()
            rock.life_line = 500 + len(self.rocks) * 10
            rock.pos = self.create_random_pos(self.width, self.height)
            self.add_widget(rock)
            self.rocks.append(rock)
        for rock in self.rocks:
            for attractor in self.attractors:
                rock.accelerate_to(attractor)
            rock.move()

    def on_touch_down(self, touch):
        new_attractor = Attractor()
        new_attractor.pos = touch.pos
        self.add_widget(new_attractor)
        self.attractors.append(new_attractor)


class AttractionApp(App):
    def build(self):
        runner = Runner()
        # Clock.schedule_once(runner.build, 0)
        Clock.schedule_interval(runner.update, 1.0 / 30.0)
        return runner


if __name__ == '__main__':
    AttractionApp().run()
