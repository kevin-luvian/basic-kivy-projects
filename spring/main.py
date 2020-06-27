from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import OptionProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.uix.behaviors import DragBehavior
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from math import sqrt, pow, degrees, atan2
from random import randint, randrange


class Rope(Widget):
    points = ListProperty([])

    def get_pivot(self):
        return self.points[0]

    def get_length(self):
        len_x = self.points[1][0] - self.points[0][0]
        len_y = self.points[1][1] - self.points[0][1]
        return sqrt(pow(len_x, 2) + pow(len_y, 2))

    def get_angle(self):
        len_x = self.points[1][0] - self.points[0][0]
        len_y = self.points[1][1] - self.points[0][1]
        return degrees(atan2(len_y, len_x))

    def update_target(self, target_point):
        self.points[1] = target_point


class Ball(Widget):
    # velocity of the ball on x and y axis
    velocity = Vector(0, 0)

    # ``move`` function will move the ball one step.
    def move(self):
        self.pos = self.velocity + self.pos


class Canvas(Widget):
    k = 0.01
    last_length = 0
    ball = ObjectProperty(None)
    rope = ObjectProperty(None)

    is_count = False
    count = NumericProperty(0)

    def change_rope_points(self, ball_obj, center):
        self.rope.update_target(center)

    def build(self, *args):
        point_x = randint(0, self.width)
        point_y = randint(0, self.height)
        self.ball.pos = (point_x, point_y)
        self.ball.velocity = Vector(0, randint(0, 100))
        self.rope.points = [[self.center_x, self.center_y], [self.ball.center_x, self.ball.center_y]]
        self.ball.bind(center=self.change_rope_points)

    def update(self, fps):
        length = self.rope.get_length()
        speed = length * self.k * -1
        new_velocity = Vector(speed, 0).rotate(self.rope.get_angle())
        self.ball.velocity = (self.ball.velocity + new_velocity) * 0.99005
        self.ball.move()

        # print('length: %s' % length)
        if not self.is_count and length > self.last_length:
            self.count += 1
            self.is_count = True
        elif length < self.last_length:
            self.is_count = False
        self.last_length = length

    def on_touch_move(self, touch):
        self.ball.center = (touch.x, touch.y)
        self.ball.velocity = Vector(0, randint(0, 100))
        self.count = 0


class SpringApp(App):
    def build(self):
        canvas = Canvas()
        Clock.schedule_once(canvas.build, 0)
        Clock.schedule_interval(canvas.update, 1.0 / 60.0)
        return canvas


if __name__ == '__main__':
    SpringApp().run()
