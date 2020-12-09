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
        neighbour_counter = 0
        separation_counter = 0
        close_counter = 0
        aggregate_velocity = None
        aggregate_position = None
        aggregate_separation = [0, 0]
        for boid in surrounding_boids:
            dist = Vector(self.pos).distance(boid.pos)
            if boid != self and const.BOID_VISIBILITY_RADIUS > dist:
                neighbour_counter += 1
                if neighbour_counter == 1:
                    aggregate_velocity = boid.velocity
                    aggregate_position = boid.pos
                else:
                    aggregate_velocity = self.add_2d_array(aggregate_velocity, boid.velocity)
                    aggregate_position = self.add_2d_array(aggregate_position, boid.pos)

                if 0 < dist < const.BOID_SEPARATION_RADIUS:
                    separation_counter += 1
                    aggregate_separation = self.separation_velocity_to_boid(boid)
                    if dist < 15:
                        close_counter += 1

        if neighbour_counter > 0:
            average_velocity = self.mult_2d_array(aggregate_velocity, 1 / neighbour_counter)
            average_position = self.mult_2d_array(aggregate_position, 1 / neighbour_counter)
            if separation_counter > 0:
                average_separation = self.mult_2d_array(aggregate_separation, 1 / separation_counter)
            else:
                average_separation = aggregate_separation

            average_velocity_vector = Vector(
                self.sub_2d_array(average_velocity, self.velocity)).normalize() * const.ALIGNMENT_MULT
            average_position_vector = Vector(
                self.sub_2d_array(average_position, self.pos)).normalize() * const.COHESION_MULT
            average_separation_vector = Vector(average_separation).normalize() * const.SEPARATION_MULT

            if close_counter > 0:
                average_separation_vector *= 100

            self.acceleration = average_velocity_vector + average_position_vector + average_separation_vector

    def separation_velocity_to_boid(self, target_boid):
        dist = Vector(self.pos).distance(target_boid.pos)
        v_diff = Vector(self.sub_2d_array(self.pos, target_boid.pos))
        # print("Diff raw", v_diff)
        v_diff = v_diff.normalize()
        # print("Diff normal", v_diff)
        # print("Dist", dist)
        return self.mult_2d_array(v_diff, dist)

    def mult_2d_array(self, arr, mult):
        return [arr[0] * mult, arr[1] * mult]

    def add_2d_array(self, arr_a, arr_b):
        return [arr_a[0] + arr_b[0], arr_a[1] + arr_b[1]]

    def sub_2d_array(self, arr_a, arr_b):
        return [arr_a[0] - arr_b[0], arr_a[1] - arr_b[1]]

    # def normalize(self, x_max, x_min, x):
    #     return (x - x_min) / x_max - x_min


class Runner(Widget):
    boids = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self, *args):
        for i in range(0, 50):
            new_boid = Boid()
            new_boid.set_constraints(self.width, self.height)
            new_boid.pos = self.new_boid_pos()
            self.add_widget(new_boid)
            self.boids.append(new_boid)

    def new_boid_pos(self):
        ran = 100
        return [randint(self.width / 2 - ran, self.width / 2 + ran),
                randint(self.height / 2 - ran, self.height / 2 + ran)]

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
        Clock.schedule_once(runner.build, 0)
        Clock.schedule_interval(runner.clock_update, 1.0 / 60.0)
        return runner


if __name__ == '__main__':
    FlockingApp().run()
