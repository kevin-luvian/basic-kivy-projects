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


class Attractor(Widget):
    pos = ListProperty([0, 0])
    weight = 0.02
    repulsion_radius = 20

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            self.pos = (touch.x - self.center_x, touch.y - self.center_y)

    def rock_acceleration(self, rock):
        center_pos = self.pos + self.center
        vector_line = Vector(center_pos[0] - rock.pos[0] + rock.center_x,
                             center_pos[1] - rock.pos[1] + rock.center_y)

        # if rock.pos[0] + rock.center_x - center_pos[0] < self.repulsion_radius and \
        #         rock.pos[1] + rock.center_y - center_pos[1] < self.repulsion_radius:
        #     vector_line *= -0.05
        #     return vector_line

        vector_line *= self.weight / vector_line.length()
        return vector_line


class Rock(Widget):
    id = 0
    path = ListProperty([])
    pos = ListProperty([0, 0])
    acceleration = Vector(0, 0)
    velocity = Vector(0, 0)

    def get_angle(self, point):
        len_x = point[0] - self.pos[0]
        len_y = point[1] - self.pos[1]
        return degrees(atan2(len_y, len_x))

    def accelerate_once(self):
        self.velocity = self.velocity + self.acceleration
        self.acceleration = self.acceleration * 0

    def accelerate_to(self, attractor):
        self.acceleration = self.acceleration + attractor.rock_acceleration(self)

    def move(self):
        self.accelerate_once()
        self.pos = Vector(self.pos) + self.velocity
        self.path.append(self.pos)
        if self.pos[0] < 0 or self.pos[0] > self.parent.width:
            self.pos[0] = abs(self.parent.width - self.pos[0])
        if self.pos[1] < 0 or self.pos[1] > self.parent.height:
            self.pos[1] = abs(self.parent.height - self.pos[1])


class Runner(Widget):
    rocks = []
    attractors = []

    def on_start(self):
        print("im starting")

    def build(self, *args):
        for i in range(300):
            rock = Rock()
            rock.id = i
            rock.pos = [randint(self.center_x - 300, self.center_x + 300),
                        randint(self.center_y - 300, self.center_y + 300)]
            # rock.pos = [500, 200]
            self.add_widget(rock)
            self.rocks.append(rock)

    def update(self, *args):
        for attractor in self.attractors:
            for rock in self.rocks:
                rock.accelerate_to(attractor)
        for rock in self.rocks:
            rock.move()

    def on_touch_down(self, touch):
        new_attractor = Attractor()
        new_attractor.pos = touch.pos
        self.add_widget(new_attractor)
        self.attractors.append(new_attractor)


class AttractionApp(App):
    def build(self):
        runner = Runner()
        Clock.schedule_once(runner.build, 0)
        Clock.schedule_interval(runner.update, 1.0 / 30.0)
        return runner


if __name__ == '__main__':
    AttractionApp().run()
