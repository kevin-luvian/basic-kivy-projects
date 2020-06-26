from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from random import randint


class PongPaddle(Widget):
    score = NumericProperty(0)

    def ball_bounce(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            vel = Vector(-1.2 * vx, vy)
            ball.velocity = vel.x, vel.y + offset


class PongBall(Widget):
    # velocity of the ball on x and y axis
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    # ``move`` function will move the ball one step.
    def move(self):
        self.pos = Vector(*self.velocity) + self.pos


class PongGame(Widget):
    ball = ObjectProperty(None)
    player_1 = ObjectProperty(None)
    player_2 = ObjectProperty(None)

    def serve_ball(self):
        self.ball.center = self.center
        self.ball.velocity = Vector(5, 0).rotate(randint(0, 360))

    def update(self, fps):
        self.ball.move()
        self.player_1.ball_bounce(self.ball)
        self.player_2.ball_bounce(self.ball)

        if (self.ball.y < 0) or (self.ball.top > self.height):
            self.ball.velocity_y *= -1

        if self.ball.center_x < 0:
            self.player_2.score += 1
            self.serve_ball()

        elif self.ball.center_x > self.width:
            self.player_1.score += 1
            self.serve_ball()

    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player_1.center_y = touch.y
        if touch.x > self.width * 2 / 3:
            self.player_2.center_y = touch.y

        #force reset on ball touch
        #if self.ball.x < touch.x < self.ball.right and self.ball.y < touch.y < self.ball.top:
        #   self.serve_ball()


class PongApp(App):
    def build(self):
        game = PongGame()
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


if __name__ == '__main__':
    PongApp().run()
