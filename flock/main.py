from concurrent.futures.thread import ThreadPoolExecutor
from random import randint

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget

import const
import quadtree
from boid import Boid


class Runner(Widget):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.boids = []
        self.bind(size=self.on_size_change)

    def on_size_change(self, *args):
        for boid in self.boids:
            boid.set_constraints(self.width, self.height)

    def build(self, *args):
        for i in range(0, const.INITIAL_BOID_SIZE):
            new_boid = Boid()
            new_boid.set_constraints(self.width, self.height)
            # new_boid.pos = self.new_boid_pos()
            new_boid.pos = [i*5, i*5]
            self.add_widget(new_boid)
            self.boids.append(new_boid)

    def new_boid_pos(self):
        ran = 100
        return [randint(self.width / 2 - ran, self.width / 2 + ran),
                randint(self.height / 2 - ran, self.height / 2 + ran)]

    def clock_update(self, *args):
        qtree = quadtree.generate_quadtree(self.boids, self.width, self.height)
        for boid in self.boids:
            radius = quadtree.create_boid_visibility_radius(boid)
            surrounding_boid = qtree.query(radius)
            boid.check_surrounding_boids(surrounding_boid)
            # print("Surround", "x", boid.pos[0], "y", boid.pos[1], len(surrounding_boid))
            # print("Radius", radius.x, radius.y, radius.w, radius.h)

        # with ThreadPoolExecutor(max_workers=10) as executor:
        #     for boid in self.boids:
        #         executor.submit(boid.move)
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
