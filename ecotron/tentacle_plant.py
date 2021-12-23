from director import Script, script_with_async_step, script_with_step
from .widget import MultiWidget, PausingActor
import random
import value_source

ANGLE_WELDING_MIN = 120
ANGLE_WELDING_MAX = 180
ANGLE_HEAD_MIN = 100
ANGLE_HEAD_MAX = 120
ANGLE_OUTSIDE_MIN = 0
ANGLE_OUTSIDE_MAX = 100

SERVO_MOVE_SPEED = 0.3


class TentacleActor(PausingActor):
    def __init__(self, plant, servo, angle_range_std, speed_range_std, angle_range_agitated, speed_range_agitated, initial):
        PausingActor.__init__(self, min_idle_time=0, max_idle_time=1)
        self._plant = plant
        self._servo = servo

        self._angle_range_std = angle_range_std
        self._speed_range_std = speed_range_std

        self._angle_range_agitated = angle_range_agitated
        self._speed_range_agitated = speed_range_agitated

        self._agitated = False

        self._servo.angle = initial

    def do_action(self, callback):
        cur_angle = self._servo.angle

        a_f, a_t = self._angle_range_agitated if self._plant._agitated else self._angle_range_std
        s_f, s_t = self._speed_range_agitated if self._plant._agitated else self._speed_range_std

        new_angle = random.uniform(a_f, a_t)

        speed = random.uniform(s_f, s_t)

        while (abs(new_angle - cur_angle) < 5):
            new_angle = random.randint(a_f, a_t)

        self._execute(script_with_async_step(lambda c: self._servo.move_to(
            new_angle, speed, callback
        )))

    def move_to(self, angle, speed, callback = lambda: None):
        s = Script()

        s.add_async_step(lambda c: self._servo.move_to(
            angle, speed, callback=c
        ))
        s.add_step(callback)
        self.force_script(s)

    def when_turn_off(self):
        print("plant off")
        PausingActor.when_turn_off(self)



class TentaclePlant(MultiWidget):

    def __init__(self, stretch_servo, rotate_servo, uprighter_servo):
        self._uprighter_servo = uprighter_servo
        self._agitated = False

        self._stretch = TentacleActor(self, stretch_servo,
            angle_range_std=(100, 140), speed_range_std=(0.1, 0.2),
            angle_range_agitated=(0, 120), speed_range_agitated=(0.1, 10),
            initial = 140
        )

        self._rotate = TentacleActor(self, rotate_servo,
            angle_range_std=(80, 120), speed_range_std=(0.1, 0.2),
            angle_range_agitated=(60, 140), speed_range_agitated=(0.1, 10),
            initial=110
        )

        self._uprighter_servo.move_to(20, 0.5)

        MultiWidget.__init__(self, self._stretch, self._rotate)

    def toggle_attack(self):
        if not self._on:
            return
        if self._agitated:
            self.peace()
        else:
            self.breakout()


    def breakout(self):
        self._stretch.move_to(0, 1)
        self._agitated = True

    def peace(self, callback=lambda: None):
        self._agitated = False

        self._rotate.move_to(110, 1)
        self._stretch.move_to(140, 2)

        self._uprighter_servo.move_to(120, 0.5, lambda: self._uprighter_servo.move_to(20, 0.5, callback))

    def when_turn_off(self):
        MultiWidget.when_turn_off(self)
        if self._agitated:
            self._agitated = False
            self._rotate._servo.move_to(110, 1)
            self._stretch._servo.move_to(140, 2)
            self._uprighter_servo.move_to(120, 0.5, lambda: self._uprighter_servo.move_to(20, 0.5))








