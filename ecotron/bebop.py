from ecotron.widget import MultiWidget, PausingActor
import random
from director import Script
from utils import translate
from ecotron.robot import RobotHead
from beeper.beeps2 import bebop_speech

PLANT_POS_TO_ANGLE = [
    (2, 0),
    (2.7, 10),
    (3, 20),
    (3.5, 30),
    (3.7, 40),
    (4, 50),
    (4.5, 60),
    (5.2, 70),
    (6, 80),
    (6.5, 90),
    (6.8, 100),
    (7, 110),
    (7.5, 120),
    (7.8, 130),
    (8, 140),
    (8.5, 150),
    (9, 160),
    (10, 170),
    (11, 180),
]

def pos_to_angle(belt_pos):
    prev_pos = 0
    prev_angle = 0
    for (pos, angle) in PLANT_POS_TO_ANGLE:
        if belt_pos < pos:
            return translate(belt_pos, prev_pos, pos, prev_angle, angle)
        prev_pos = pos
        prev_angle = angle
    return 180


class BebopActor(PausingActor):
    def __init__(self, servo):
        PausingActor.__init__(self,
            min_idle_time=0.5,
            max_idle_time=2.5
        )
        self._servo = servo
        self._conveyor = None

    def observe(self, c):
        self._conveyor = c

    def do_action(self, callback):
        if self._conveyor != None and random.random() < 0.8:
            self._track_plant(callback)
        else:
            self._random_rotation(callback)

    def _random_rotation(self, callback):
        self._servo.move_to(random.randint(20, 160), speed=0.3, callback=callback)

    def _rotate_to_plant(self, plant, callback):
        plant_angle = pos_to_angle(plant.belt_position())
        self._servo.move_to(plant_angle, speed=0.5, callback=callback)

    def _track_plant(self, callback):
        plants = [p for p in self._conveyor.plants if p.belt_position() < 8]
        plant_to_track = random.choice(plants)
        tracking_duration = random.uniform(2, 8)
        tracking_time_resolution = 0.05

        s = Script()
        for _ in range(int(tracking_duration / tracking_time_resolution)):
            s.add_async_step(lambda c: self._rotate_to_plant(plant_to_track, c))
            s.add_sleep(tracking_time_resolution)
        s.execute(callback)


class Bebop(MultiWidget):

    def __init__(self, servo, pwm_led):
        self._head = RobotHead(eye_led=pwm_led, speech=bebop_speech(), volume=0.3)
        self._actor = BebopActor(servo)
        MultiWidget.__init__(self, self._head, self._actor)

    def observe_conveyor(self, c):
        self._actor.observe(c)

