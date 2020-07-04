from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ListProperty, StringProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from random import randint

SEGMENT_SIZE = 20


class Food(Widget):
    pos = ListProperty([0, 0])
    size = ListProperty([SEGMENT_SIZE, SEGMENT_SIZE])


class Segment(Widget):
    pos = ListProperty([0, 0])
    color = ListProperty([1, 1, 1])
    size = ListProperty([SEGMENT_SIZE, SEGMENT_SIZE])
    velocity = Vector(0, 0)

    def change_dir(self, command, has_body):
        new_velocity = Vector(0, 0)
        if command == 'up':
            new_velocity = Vector(0, SEGMENT_SIZE)
        elif command == 'down':
            new_velocity = Vector(0, -SEGMENT_SIZE)
        elif command == 'right':
            new_velocity = Vector(SEGMENT_SIZE, 0)
        elif command == 'left':
            new_velocity = Vector(-SEGMENT_SIZE, 0)
        if not has_body or (has_body and self.velocity != new_velocity * -1):
            self.velocity = new_velocity

    def move(self):
        self.pos = Vector(self.pos) + self.velocity


class Runner(Widget):
    snake_head = None
    snake_body = []
    food = None
    commands = []
    is_update = True
    label = StringProperty("Snake Body: 0")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._on_keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_key_down)

    def _on_keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_key_down)
        self._keyboard = None

    def _on_key_down(self, keyboard, keycode, *args):
        # print('The key', keycode[1], 'have been pressed')
        # print(self.snake_head.pos)
        if keycode[1] == 'escape':
            keyboard.release()
        elif keycode[1] == 'spacebar':
            self.is_update = not self.is_update
        elif self.is_update and keycode[1] in ['up', 'down', 'left', 'right']:
            if keycode[1] not in self.commands:
                self.commands.append(keycode[1])

    def create_empty_pos(self):
        checker = True
        new_pos = None
        while checker:
            new_pos = [randint(0, (self.width - 50) // SEGMENT_SIZE) * SEGMENT_SIZE,
                       randint(0, (self.height - 50) // SEGMENT_SIZE) * SEGMENT_SIZE]
            checker = False
            if self.snake_head.pos == new_pos:
                checker = True
            for segment in self.snake_body:
                if segment.pos == new_pos:
                    checker = True
                    break
        return new_pos

    def create_new_segment(self, pos):
        new_segment = Segment()
        new_segment.pos = pos
        self.snake_body.append(new_segment)
        self.add_widget(new_segment)

    def build(self, *args):
        self.snake_head = Segment()
        self.snake_head.color = [52 / 255, 158 / 255, 235 / 255]
        self.snake_head.pos = [randint(0, self.width // SEGMENT_SIZE) * SEGMENT_SIZE,
                               randint(0, self.height // SEGMENT_SIZE) * SEGMENT_SIZE]
        self.food = Food()
        self.food.pos = self.create_empty_pos()
        self.add_widget(self.food)
        self.add_widget(self.snake_head)

    def update(self, *args):
        if self.is_update:
            if len(self.commands) > 0:
                self.snake_head.change_dir(self.commands.pop(0), len(self.snake_body) > 0)
            new_pos = self.snake_head.pos
            for segment in self.snake_body:
                temp_pos = segment.pos
                if Vector(self.snake_head.pos) + self.snake_head.velocity == temp_pos:
                    self.label = "You is ded!"
                    self.is_update = False
                segment.pos = new_pos
                new_pos = temp_pos
            self.snake_head.move()
            if self.snake_head.pos == self.food.pos:
                self.create_new_segment(new_pos)
                # self.food.pos = self.create_empty_pos()
                self.label = "Snake Body: " + str(len(self.snake_body))

            if self.snake_head.pos[0] < 0:
                self.snake_head.pos = [self.width, self.snake_head.pos[1]]
            elif self.snake_head.pos[0] >= self.width:
                self.snake_head.pos = [0, self.snake_head.pos[1]]
            if self.snake_head.pos[1] < 0:
                self.snake_head.pos = [self.snake_head.pos[0], self.height]
            elif self.snake_head.pos[1] >= self.height:
                self.snake_head.pos = [self.snake_head.pos[0], 0]


class SnakeApp(App):
    def build(self):
        runner = Runner()
        Clock.schedule_once(runner.build, 0)
        Clock.schedule_interval(runner.update, 1.0 / 30.0)
        return runner


if __name__ == '__main__':
    SnakeApp().run()
