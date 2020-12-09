import math
import unittest

from kivy.vector import Vector

from main import Boid


class TestBoid(unittest.TestCase):

    def test_vector_velocity(self):
        v_a = Vector(5, 0)
        v_a = v_a.rotate(90)
        v_proj = Vector(1, 0)
        v_a_angle = v_proj.angle(v_a)
        print("va angle", v_a_angle)
        v_new = v_a.rotate(v_a_angle)
        print("v new", v_new)
        v_y = v_new.y if v_new.y < 5 else 5
        v_new = Vector(v_new.x, v_y)
        print("v new", v_new)

    def test_check(self):
        v_a = Vector(5, 0)
        print(v_a[0])
        print(v_a[1])


if __name__ == '__main__':
    unittest.main()
