from ecotron.widget import PausingActor
import random

class Stairsdude(PausingActor):
    def __init__(self, servo):
        PausingActor.__init__(self,
            min_idle_time = 2,
            max_idle_time = 5
        )
        self._servo = servo

    def random_rotation(self):
        self._random_rotation(random.uniform(0.15, 0.3))

    def do_action(self, callback):
        self._random_rotation(random.uniform(0.15, 0.3), callback)

    def _random_rotation(self, speed=0.3, callback=lambda:None):
        self._servo.move_to(random.randint(0, 180), speed=speed, callback=callback)
