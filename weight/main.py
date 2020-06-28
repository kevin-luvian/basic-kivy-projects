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

DELTA_TIME = 1.0 / 60.0
MAX_BALL_SPEED = 100.0
GRAVITY = 0.9
FRICTION = 0.9


class Ball(Widget):
    # velocity of the ball on x and y axis
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def apply_force(self, force_x, force_y):
        self.velocity_x += force_x
        self.velocity_y += force_y

    # ``move`` function will move the ball one step.
    def move(self):
        self.pos = Vector(*self.velocity) + self.pos


class Simulation(Widget):

    def __init__(self, **kwargs):
        super(Simulation, self).__init__(**kwargs)
        self.balls = [Ball()]

    def build(self, *args):
        self.add_widget(self.balls[0])
        self.balls[0].pos = (self.center_x, self.height - 200)
        self.balls[0].velocity_x -= 3

    def update(self, *args):
        for ball in self.balls:
            ball.apply_force(0, -GRAVITY)
            if ball.y <= 0:
                ball.y = 0
                ball.velocity_y *= -FRICTION
            if ball.x < 0 or ball.right > self.width:
                if ball.x <= 0:
                    ball.x = 0
                ball.velocity_x *= -1

            ball.move()

    def on_touch_down(self, touch):
        print("touched")
        for ball in self.balls:
            ball.apply_force(2, 0)


class WeightApp(App):
    def build(self):
        simulation = Simulation()
        Clock.schedule_once(simulation.build, 0)
        Clock.schedule_interval(simulation.update, 1.0 / 60.0)
        return simulation


if __name__ == '__main__':
    WeightApp().run()
