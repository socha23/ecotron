from ecotron.robot import RobotHead
from beeper.beeps2 import eddard_speech
from director import Script
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

class RepairActor(PausingActor):
    def __init__(self, servo, light):
        PausingActor.__init__(self, min_idle_time=0.5, max_idle_time=3)
        self._welder_servo = servo
        self._welder_light = light

    def do_action(self, callback):
        action = random.randint(0, 10)
        if action < 6:
            self._do_some_welding(callback)
        elif action < 8:
            self._look_at_head(callback)
        else:
            self._look_at_outside(callback)

    def _look_at_head(self, callback):
        self._execute(Script()
            .add_async_step(lambda c: self._welder_servo.move_to(random.randrange(ANGLE_HEAD_MIN, ANGLE_HEAD_MAX), SERVO_MOVE_SPEED, c))
            .add_step(callback)
        )

    def _look_at_outside(self, callback):
        self._execute(Script()
            .add_async_step(lambda c: self._welder_servo.move_to(random.randint(ANGLE_OUTSIDE_MIN, ANGLE_OUTSIDE_MAX), SERVO_MOVE_SPEED, c))
            .add_step(callback)
        )

    def _do_some_welding(self, callback):
        script = Script()

        script.add_async_step(lambda c: self._welder_servo.move_to(random.randint(ANGLE_WELDING_MIN, ANGLE_WELDING_MAX), SERVO_MOVE_SPEED, c))
        script.add_sleep(0.2)

        for _ in range(random.randint(3, 7)):
            script.add_async_step(lambda c: self._welder_servo.move_to(random.randint(ANGLE_WELDING_MIN, ANGLE_WELDING_MAX), SERVO_MOVE_SPEED, c))
            script.add_sleep(0.2)

            ONE_BLINK_DURATION = 0.1

            repetitions = random.randint(2, 20)
            time = repetitions * ONE_BLINK_DURATION

            script.add_step(lambda: self._welder_light.set_source(value_source.repeated_blink(how_many = repetitions, duration = ONE_BLINK_DURATION)))
            script.add_sleep(time + 0.5)

        script.add_step(callback)
        self._execute(script)


class RepairTable(MultiWidget):

    def __init__(self, robot_light, welder_light, welder_servo):
        self._eddard_head = RobotHead(robot_light, eddard_speech(), standby_brightness=0.4, volume=0.2)
        self._actor = RepairActor(welder_servo, welder_light)

        MultiWidget.__init__(self, self._actor, self._eddard_head)
