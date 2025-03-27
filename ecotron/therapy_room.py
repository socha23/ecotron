from director import Script
from .widget import Widget, MultiWidget, PausingActor
from beeper.beeps2 import dangler_speech
from ecotron.robot import RobotHead
from .properties import DEFAULT_ECOTRON_PROPERTIES
from value_source import FadeInOut, Constant, ValueSource, Lambda, AlwaysOff, Sine
from tick_aware import TickAware
from components.led import PWMLED
from random import random


POS_UPDATE_DELTA = 5

MOVE_SPEED = 0.2

FIRST_PLANT_CORRECTION = 0
LAST_PLANT_CORRECTION = 0

POS_PLANT = [0, 120, 240, 360]

ON_TURN_ON_MOVE = -380


class TherapyRoom(MultiWidget):
    def __init__(self, robot_motor, servo_kit, properties=DEFAULT_ECOTRON_PROPERTIES):
        self._plants = [
            PlantBed(
                0,
                PWMLED(servo_kit._pca.channels[0]),
                PWMLED(servo_kit._pca.channels[1]),
                on_alert=self.on_alert,
                reset_move=True),
            PlantBed(
                120,
                PWMLED(servo_kit._pca.channels[2]),
                PWMLED(servo_kit._pca.channels[3]),
                on_alert=self.on_alert,
                ),
            PlantBed(
                240,
                PWMLED(servo_kit._pca.channels[4]),
                PWMLED(servo_kit._pca.channels[5]),
                on_alert=self.on_alert,
                ),
            PlantBed(
                360,
                PWMLED(servo_kit._pca.channels[6]),
                PWMLED(servo_kit._pca.channels[7]),
                on_alert=self.on_alert,
                reset_move=True),
        ]
        self._danglerbot = DanglerBot(robot_motor, PWMLED(servo_kit._pca.channels[8]), PWMLED(servo_kit._pca.channels[9]), self._plants[0])

        MultiWidget.__init__(self, self._danglerbot, *self._plants)

        self.bind_to_property(properties.therapy_room_on)

        self._current_plant_idx = 0

        self._alert_queue = []
        self._responding_to_alert = False

    def act_on_alert(self):
        if self._responding_to_alert or len(self._alert_queue) == 0:
            return
        self._responding_to_alert = True
        plant = self._alert_queue.pop(0)
        self._current_plant_idx = self._plants.index(plant)
        (Script()
            .add_sleep(0.1 + random())
            .add_async_step(lambda c: self._danglerbot.move_to_plant_bed(plant, on_complete=c))
            .add_async_step(lambda c: self._danglerbot.spray(on_complete=c))
            .add_step(self.finish_acting_on_alert)
            ).execute()

    def finish_acting_on_alert(self):
        self._responding_to_alert = False
        self.act_on_alert()

    def on_alert(self, plant):
        self._alert_queue.append(plant)
        self.act_on_alert()

    def when_turn_on(self):
        MultiWidget.when_turn_on(self)
        self._responding_to_alert = False
        self._alert_queue = []


    def next_plant(self):
        if self._danglerbot.busy() or self._current_plant_idx == len(self._plants) - 1:
            return
        self._current_plant_idx += 1
        self._danglerbot.move_to_plant_bed(self._plants[self._current_plant_idx])

    def prev_plant(self):
        if self._danglerbot.busy() or self._current_plant_idx == 0:
            return
        self._current_plant_idx -= 1
        self._danglerbot.move_to_plant_bed(self._plants[self._current_plant_idx])

    def spray(self):
        if self._danglerbot.busy():
            return
        self._danglerbot.spray()

class PlantBed(Widget, TickAware):
    def __init__(self, position, nutrition_light, alert_light, on_alert=lambda x: None, reset_move=False):
        Widget.__init__(self)
        TickAware.__init__(self)
        self.position = position
        self._nutrition_light = nutrition_light
        self._alert_light = alert_light

        self._consumption = self._random_consumption()
        self._feeding_rate = 0.4
        self._alert_level = 0.2

        self._nutrition = 1
        self._alert_on = False
        self._feeding_on = False

        self.reset_move = reset_move
        self._on_alert = on_alert

    def _reset(self):
        self._nutrition = 0.5 + 0.5 * random()
        self._alert_on = False
        self._feeding_on = False

    def _nutrition_light_value(self):
        return self._nutrition * 0.5

    def when_turn_on(self):
        self._reset()
        self._nutrition_light.source = Lambda(self._nutrition_light_value)
        self._alert_light.source = AlwaysOff()

    def when_turn_off(self):
        self._nutrition_light.source = AlwaysOff()
        self._alert_light.source = AlwaysOff()

    def start_feeding(self):
        self._feeding_on = True

    def stop_feeding(self):
        self._feeding_on = False

        self._consumption = self._random_consumption()

    def _random_consumption(self):
        return 0.02 + random() * 0.03

    def tick(self, cur_s, delta_s):
        if self.on and not self._feeding_on:
            self._nutrition = max(self._nutrition - delta_s * self._consumption, 0)
            if self._nutrition <= self._alert_level and not self._alert_on:
                self.start_alert()

        if self.on and self._feeding_on:
            self._nutrition = min(self._nutrition + delta_s * self._feeding_rate, 1)
            if self._nutrition > self._alert_level and self._alert_on:
                self.stop_alert()

    def start_alert(self):
        self._alert_on = True
        self._on_alert(self)
        self._alert_light.source = Sine(0.5, Constant(0.5))

    def stop_alert(self):
        self._alert_on = False
        self._alert_light.source = AlwaysOff()




class DanglerBot(MultiWidget):
    def __init__(self, motor, robot_light, sprayer_light, start_plant):

        self._head = RobotHead(robot_light, dangler_speech(),
            standby_brightness=0.2,
            volume=0.2,
            max_idle_time=5)

        MultiWidget.__init__(self, self._head)

        self._sprayer_light = sprayer_light
        self._motor = motor
        self._current_plant = start_plant

        self._during_move = True

        (Script()
            .add_step(lambda: motor.set_feedback_mode(POS_UPDATE_DELTA))
            .add_sleep(0.1)
            .add_step(motor.reset_position)
            .add_async_step(lambda c: motor.goto_absolute_position(ON_TURN_ON_MOVE, MOVE_SPEED, on_complete=c))
            .add_step(motor.reset_position)
            .add_step(self._on_finish_move)
        ).execute()

    def busy(self):
        return self._during_move

    def spray(self, duration = 3, brightness = 1, fade_duration = 0.5, on_complete = lambda: None):
        self._during_move = True
        source = FadeInOut(fade_duration, Constant(brightness))
        self._sprayer_light.set_source(source)
        (Script()
            .add_step(self._current_plant.start_feeding)
            .add_step(source.fade_in)
            .add_sleep(duration - fade_duration)
            .add_step(source.fade_out)
            .add_sleep(fade_duration)
            .add_step(self._current_plant.stop_feeding)
            .add_step(self._on_finish_move)
        ).execute(on_complete)

    def move_to_plant_bed(self, plant, on_complete = lambda: None):
        self._during_move = True
        self._current_plant = plant
        after_move = lambda: None
        motor = self._motor
        if plant.reset_move:
            after_move = lambda: motor.reset_position(plant.position)
        (Script()
            .add_async_step(lambda c: self._motor.goto_absolute_position(
                plant.position,
                speed=MOVE_SPEED,
                on_complete=c))
            .add_step(after_move)
            .add_step(self._on_finish_move)
        ).execute(on_complete)

    def _on_finish_move(self):
        self._during_move = False
