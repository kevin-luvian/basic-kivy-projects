import math
from random import random, randint

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ListProperty
from kivy.uix.widget import Widget
from kivy.vector import Vector

import const


class Boid(Widget):
    pos = ListProperty([0, 0])
    acceleration = Vector(0, 0)
    # updated_velocity = Vector(0, 0)
    velocity = Vector(0, 0)
    vision_radius = 30
    constraint_x = 0
    constraint_y = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initial_random_velocity()

    def initial_random_velocity(self):
        vect = Vector(const.SPEED, 0)
        self.velocity = vect.rotate(randint(0, 360))

    def accelerate_once(self):
        self.velocity = self.velocity + self.acceleration * const.ACCELERATION_MULT
        self.acceleration *= 0

    def move(self):
        self.accelerate_once()
        # self.velocity = self.updated_velocity
        self.velocity = self.velocity_to_max(self.velocity, const.SPEED)
        self.pos = Vector(self.pos) + self.velocity
        self.check_constraint_pos(0, self.constraint_x)
        self.check_constraint_pos(1, self.constraint_y)

    def velocity_to_max(self, velocity, max_val):
        v_angle = Vector(1, 0).angle(velocity)
        v_rotate = velocity.rotate(v_angle)
        v_x = v_rotate.x
        if v_x >= 0:
            v_x = max_val
        elif v_x < 0:
            v_x = -max_val
        return Vector(v_x, 0).rotate(-v_angle)

    def check_constraint_pos(self, pos_index, constraint_value):
        if self.pos[pos_index] - constraint_value > 10:
            self.pos[pos_index] = 0
        elif constraint_value - self.pos[pos_index] > constraint_value + 10:
            self.pos[pos_index] = constraint_value

    def set_constraints(self, x, y):
        self.constraint_x = x
        self.constraint_y = y

    def check_surrounding_boids(self, surrounding_boids):
        average_velocity = self.velocity
        average_position = Vector(self.pos)
        average_separation = Vector(0, 0)
        initial_flag = True
        for boid in surrounding_boids:
            if boid != self and const.BOID_VISIBILITY_RADIUS > self.distance_to_position(boid.pos):
                average_velocity = self.average_velocity_to_boid(average_velocity, boid)
                # if initial_flag:
                #     average_position = Vector(boid.pos)
                #     average_separation = self.separation_velocity_to_boid(boid)
                #     initial_flag = False
                # else:
                average_position = self.average_position_to_boid(average_position, boid)
                average_separation = self.average_separation_velocity_to_boid(average_separation, boid)

        average_velocity_vector = (average_velocity - self.velocity).normalize() * const.ALIGNMENT_MULT
        average_position_vector = (average_position - Vector(self.pos)).normalize() * const.COHESION_MULT
        average_separation_vector = average_separation * const.SEPARATION_MULT
        self.acceleration = average_velocity_vector + average_position_vector + average_separation_vector
        # self.updated_velocity = average_force

    def distance_to_position(self, position):
        return Vector(self.pos).distance(position)

    def average_velocity_to_boid(self, velocity, target_boid):
        return (velocity + target_boid.velocity) / Vector(2, 2)

    def average_position_to_boid(self, position, target_boid):
        return (Vector(position) + Vector(target_boid.pos)) / Vector(2, 2)

    def average_separation_velocity_to_boid(self, average_separation, target_boid):
        separation_range = 30
        dist = Vector(self.pos).distance(target_boid.pos)
        if 0 < dist < separation_range:
            v_diff = self.separation_velocity_to_boid(target_boid)
            return (average_separation + v_diff) / Vector(2, 2)
        return average_separation

    def separation_velocity_to_boid(self, target_boid):
        dist = Vector(self.pos).distance(target_boid.pos)
        v_diff = Vector(self.pos) - Vector(target_boid.pos)
        # print("Diff raw", v_diff)
        v_diff = v_diff.normalize()
        # print("Diff normal", v_diff)
        # print("Dist", dist)
        v_diff /= dist
        # print("Diff", v_diff)
        return v_diff

    # def normalize(self, x_max, x_min, x):
    #     return (x - x_min) / x_max - x_min


class Runner(Widget):
    boids = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def clock_update(self, *args):
        for boid in self.boids:
            # for boid in self.boids:
            boid.check_surrounding_boids(self.boids)

        for boid in self.boids:
            boid.move()

    def on_touch_down(self, touch):
        new_boid = Boid()
        new_boid.set_constraints(self.width, self.height)
        new_boid.pos = touch.pos
        self.add_widget(new_boid)
        self.boids.append(new_boid)


class FlockingApp(App):
    def build(self):
        runner = Runner()
        # Clock.schedule_once(runner.build, 0)
        Clock.schedule_interval(runner.clock_update, 1.0 / 60.0)
        return runner


if __name__ == '__main__':
    FlockingApp().run()
