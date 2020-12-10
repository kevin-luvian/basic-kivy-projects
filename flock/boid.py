import math
import sys
from math import sqrt
from random import randint

from kivy.properties import ListProperty
from kivy.uix.widget import Widget
from kivy.vector import Vector

import const


class Boid(Widget):
    pos = ListProperty([0, 0])
    acceleration = Vector(0, 0)
    velocity = Vector(0, 0)
    vision_radius = 30
    constraint_x = 0
    constraint_y = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initial_random_velocity()

    def initial_random_velocity(self):
        # self.velocity = Vector(const.SPEED, 0).rotate(randint(0, 360))
        self.velocity = Vector(const.SPEED, 0).rotate(45)

    def accelerate_once(self):
        # self.velocity = self.velocity + self.velocity_to_max(self.acceleration * const.ACCELERATION_MULT, const.SPEED)
        self.velocity = self.add_2d_array(self.velocity, self.mult_2d_array(self.acceleration, const.ACCELERATION_MULT))
        self.acceleration = [0, 0]

    def move(self):
        self.accelerate_once()
        self.velocity = self.velocity_to_max(self.velocity, const.SPEED)
        self.pos = self.add_2d_array(self.pos, self.velocity)
        self.check_constraint_pos(0, self.constraint_x)
        self.check_constraint_pos(1, self.constraint_y)

    def velocity_to_max(self, velocity, max_val):
        vel_normalize = self.normalize_2d_array(velocity)
        return Vector(self.mult_2d_array(vel_normalize, max_val))

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
        aggregate_velocity = [0, 0]
        aggregate_position = [0, 0]
        aggregate_separation = [0, 0]
        for boid in surrounding_boids:
            if boid != self:
                neighbour_counter += 1

                dist = self.distance_2d_array(self.pos, boid.pos)
                if dist < const.BOID_SEPARATION_RADIUS:
                    separation_counter += 1
                    aggregate_separation = self.separation_velocity_to_boid(boid)

                if dist < const.CLOSE_SEPARATION_RADIUS:
                    close_counter += 1

                aggregate_velocity = self.add_2d_array(aggregate_velocity, boid.velocity)
                if neighbour_counter == 1:
                    aggregate_position = boid.pos
                else:
                    aggregate_position = self.add_2d_array(aggregate_position, boid.pos)

        if neighbour_counter > 0:
            average_velocity_vector = self.calc_average_velocity_vector(aggregate_velocity, neighbour_counter)
            average_position_vector = self.calc_average_position_vector(aggregate_position, neighbour_counter)
            average_separation_vector = self.calc_average_separation_vector(aggregate_separation, separation_counter)

            if close_counter > 0:
                average_separation_vector = self.mult_2d_array(self.normalize_2d_array(average_separation_vector),
                                                               const.CLOSE_SEPARATION_MULT)

            # self.acceleration = average_velocity_vector + average_position_vector + average_separation_vector
            # if close_counter > 0:
            #     self.acceleration = self.sub_2d_array(average_separation_vector,
            #                                           self.velocity)
            self.acceleration = self.sub_2d_array(
                self.multi_add_2d_array(average_velocity_vector,
                                        average_position_vector,
                                        average_separation_vector),
                self.velocity)

    def calc_average_velocity_vector(self, aggregate_velocity, count):
        avg_vel = self.mult_2d_array(aggregate_velocity, 1 / count)
        # force_normalize = self.normalize_2d_array(self.sub_2d_array(avg_vel, self.velocity))
        force_normalize = self.normalize_2d_array(avg_vel)
        return self.mult_2d_array(force_normalize, const.ALIGNMENT_MULT)

    def calc_average_position_vector(self, aggregate_position, count):
        average_position = self.mult_2d_array(aggregate_position, 1 / count)
        avg_pos_vector = self.sub_2d_array(average_position, self.pos)
        # force_normalize = self.normalize_2d_array(self.sub_2d_array(avg_pos_vector, self.velocity))
        force_normalize = self.normalize_2d_array(avg_pos_vector)
        return self.mult_2d_array(force_normalize, const.COHESION_MULT)

    def calc_average_separation_vector(self, aggregate_separation, count):
        if count == 0:
            return [0, 0]
        average_separation = self.mult_2d_array(aggregate_separation, 1 / count)
        # force_normalize = self.normalize_2d_array(self.sub_2d_array(average_separation, self.velocity))
        force_normalize = self.normalize_2d_array(average_separation)
        return self.mult_2d_array(force_normalize, const.SEPARATION_MULT)

    def separation_velocity_to_boid(self, target_boid):
        dist = self.distance_2d_array(self.pos, target_boid.pos)
        v_diff = self.normalize_2d_array(self.sub_2d_array(self.pos, target_boid.pos))
        if dist <= 7:
            return self.mult_2d_array(v_diff, 5)
        return self.mult_2d_array(v_diff, 1 / dist)

    def mult_2d_array(self, arr, mult):
        return [arr[0] * mult, arr[1] * mult]

    def add_2d_array(self, arr_a, arr_b):
        return [arr_a[0] + arr_b[0], arr_a[1] + arr_b[1]]

    def sub_2d_array(self, arr_a, arr_b):
        return [arr_a[0] - arr_b[0], arr_a[1] - arr_b[1]]

    def multi_add_2d_array(self, *arrs):
        res = [0, 0]
        for arr in arrs:
            res[0] += arr[0]
            res[1] += arr[1]
        return res

    def normalize_2d_array(self, arr):
        length = sqrt(arr[0] ** 2 + arr[1] ** 2)
        if length == 0:
            return [0, 0]
        return self.mult_2d_array(arr, 1 / length)

    def distance_2d_array(self, arr_a, arr_b):
        comb_arr = self.sub_2d_array(arr_a, arr_b)
        return sqrt(comb_arr[0] ** 2 + comb_arr[1] ** 2)
