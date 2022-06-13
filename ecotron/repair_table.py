from ecotron.robot import RobotHead
from beeper.beeps2 import eddard_speech
from director import Script
from .widget import MultiWidget, PausingActor
import random
from value_source import Multiply, Constant
import glob
from sound import Clip

ANGLE_WELDING_MIN = 120
ANGLE_WELDING_MAX = 180
ANGLE_HEAD_MIN = 100
ANGLE_HEAD_MAX = 120
ANGLE_OUTSIDE_MIN = 0
ANGLE_OUTSIDE_MAX = 70

SERVO_MOVE_SPEED = 0.3

WELDER_CLIPS = [Clip(path, stereo=[0.9, 0.3]) for path in glob.glob("./resources/electric_weld_*.ogg")]

class RepairActor(PausingActor):
    def __init__(self, servo, light):
        PausingActor.__init__(self, min_idle_time=0.2, max_idle_time=1.5)
        self._welder_servo = servo
        self._welder_light = light

    def do_action(self, callback):
        action = random.randint(0, 10)
        if action < 8:
            self._do_some_welding(callback)
        elif action < 9:
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
        clip = random.choice(WELDER_CLIPS)
        script.add_step(lambda: self._welder_light.set_source(Multiply(clip.intensity_source(), Constant(4))))
        script.add_async_step(lambda callback: clip.play(callback))
        script.add_step(callback)
        self._execute(script)


class RepairTable(MultiWidget):

    def __init__(self, robot_light, welder_light, welder_servo):
        self._eddard_head = RobotHead(robot_light, eddard_speech(), standby_brightness=0.4, volume=0.2, max_idle_time=10)
        self._actor = RepairActor(welder_servo, welder_light)

        MultiWidget.__init__(self, self._actor, self._eddard_head)
