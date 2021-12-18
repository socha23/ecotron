from value_source import Constant
from ecotron.widget import MultiWidget, PausingActor
import random
from director import Script
from ecotron.robot import RobotHead
from beeper.beeps2 import spiderbro_speech

SPEECH = spiderbro_speech()

class SpiderbroActor(PausingActor):
    def __init__(self, servo, head):
        PausingActor.__init__(self,
            min_idle_time = 2,
            max_idle_time = 5
        )
        self._servo = servo
        self._head = head

    def do_action(self, callback):
        r = random.random()
        if r < 0.2:
            self._sweep(callback)
        elif r < 0.6:
            self._random_rotation(0.4, callback)
        elif r < 0.9:
            self._random_rotation(0.7, callback)
        else:
            self._look_at_me(callback)

    def _random_rotation(self, speed=0.7, callback=lambda:None):
        self._servo.move_to(random.randint(0, 150), speed=speed, callback=callback)

    def _look_at_me(self, callback):
        (Script()
            .add_async_step(lambda c: self._servo.move_to(180, speed=0.7, callback=c))
            .add_async_step(lambda c: self._head.speak(SPEECH.beeps_random(6, 15), c))
        ).execute(callback)

    def _sweep(self, callback):
        sweep_from = 0
        sweep_to = 0
        sweep_min = 0
        sweep_max = 160
        sweep_min_distance = 80
        while abs(sweep_from - sweep_to) < sweep_min_distance:
            sweep_from = random.randint(sweep_min, sweep_max)
            sweep_to = random.randint(sweep_min, sweep_max)
        s = Script()
        s.add_async_step(lambda c: self._servo.move_to(sweep_from, speed=0.7, callback=c))
        s.add_step(lambda: self._head.set_eye_source(Constant(1)))
        s.add_sleep(2)
        s.add_async_step(lambda c: self._servo.move_to(sweep_to, speed=0.1, callback=c))
        s.add_sleep(2)
        s.add_step(lambda: self._head.restore_eye_source())
        s.execute(callback)


class Spiderbro(MultiWidget):

    def __init__(self, servo, pwm_led):
        self._head = RobotHead(eye_led=pwm_led, speech=SPEECH, volume=0.3)
        self._actor = SpiderbroActor(servo, self._head)
        MultiWidget.__init__(self, self._head, self._actor)
