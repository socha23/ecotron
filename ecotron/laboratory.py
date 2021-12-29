from director import Script, script_with_async_step, script_with_sleep, script_with_step
from ecotron.lights import Lights
from ecotron.properties import EcotronProperties
from speech import SpeechLines, say
from .widget import MultiWidget, PausingActor, Widget
import random
from value_source import Constant, Sine, AlwaysOff
import ecotron.siren
from ecotron.properties import DEFAULT_ECOTRON_PROPERTIES

ANGLE_WELDING_MIN = 120
ANGLE_WELDING_MAX = 180
ANGLE_HEAD_MIN = 100
ANGLE_HEAD_MAX = 120
ANGLE_OUTSIDE_MIN = 0
ANGLE_OUTSIDE_MAX = 100

SERVO_MOVE_SPEED = 0.3

STATE_PEACE = 0
STATE_AGITATED = 1
STATE_ATTACK = 2


class TentacleActor(PausingActor):
    def __init__(self, laboratory, servo, state_to_angle_range, state_to_speed_range, state_to_pause_range, initial, min_move_angle = 0):
        PausingActor.__init__(self, min_idle_time=0, max_idle_time=1)
        self._laboratory = laboratory
        self._servo = servo
        self._state_to_angle_range = state_to_angle_range
        self._state_to_speed_range = state_to_speed_range
        self._state_to_pause_range = state_to_pause_range
        self._servo.angle = initial
        self._min_move_angle = min_move_angle

    def do_action(self, callback):
        cur_angle = self._servo.angle
        state = self._laboratory._state
        a_f, a_t = self._state_to_angle_range[state]
        s_f, s_t = self._state_to_speed_range[state]
        new_angle = random.uniform(a_f, a_t)
        while abs(new_angle - cur_angle) < self._min_move_angle:
            new_angle = random.uniform(a_f, a_t)
        speed = random.uniform(s_f, s_t)
        self._execute(script_with_async_step(lambda c: self._servo.move_to(
            new_angle, speed, callback
        )))

    def _get_idle_time(self):
        p_f, p_t = self._state_to_pause_range[self._laboratory._state]
        return random.uniform(p_f, p_t)

    def move_to(self, angle, speed):
        self.force_script(script_with_async_step(self.move_async_step(angle, speed)))

    def move_async_step(self, angle, speed):
        return lambda c: self._servo.move_to(angle, speed, c)

    def when_turn_off(self):
        print("plant off")
        PausingActor.when_turn_off(self)


class TentaclePlant(MultiWidget):

    def __init__(self, laboratory, stretch_servo, rotate_servo, uprighter_servo):
        self._uprighter_servo = uprighter_servo
        self._laboratory = laboratory
        self._stretch = TentacleActor(laboratory, stretch_servo,
            state_to_angle_range= {
                STATE_PEACE: (100, 140),
                STATE_AGITATED: (100, 140),
                STATE_ATTACK: (0, 120)
            },
            state_to_speed_range= {
                STATE_PEACE: (0.01, 0.1),
                STATE_AGITATED: (0.1, 3),
                STATE_ATTACK: (0.1, 10),
            },
            state_to_pause_range= {
                STATE_PEACE: (0.1, 0.2),
                STATE_AGITATED: (0.1, 0.2),
                STATE_ATTACK: (0.1, 0.2),
            },
            initial = 140
        )
        self._rotate = TentacleActor(laboratory, rotate_servo,
            state_to_angle_range= {
                STATE_PEACE: (80, 120),
                STATE_AGITATED: (80, 120),
                STATE_ATTACK: (60, 140)
            },
            state_to_speed_range= {
                STATE_PEACE: (0.01, 0.1),
                STATE_AGITATED: (0.1, 3),
                STATE_ATTACK: (0.1, 10),
            },
            state_to_pause_range= {
                STATE_PEACE: (0.1, 0.2),
                STATE_AGITATED: (0.1, 0.2),
                STATE_ATTACK: (0.1, 0.2),
            },
            initial=110
        )

        self._uprighter_servo.move_to(20, 0.5)
        MultiWidget.__init__(self, self._stretch, self._rotate)

    def breakout(self):
        self._stretch.force_script(Script()
            .add_async_step(self._stretch.move_async_step(0, 1))
            .add_sleep(0.5)
        )

    def _upright(self):
        s = Script()
        s.add_async_step(lambda c: self._uprighter_servo.move_to(160, 0.5, c))
        s.add_sleep(1)
        s.add_async_step(lambda c: self._uprighter_servo.move_to(20, 0.5, c))
        s.execute()


    def peace(self):
        self._rotate.move_to(110, 1)
        self._stretch.move_to(140, 2)
        self._upright()

    def when_turn_off(self):
        MultiWidget.when_turn_off(self)
        if self._laboratory._state == STATE_ATTACK:
            self._rotate._servo.move_to(110, 1)
            self._stretch._servo.move_to(140, 2)
            self._upright()


class StalkPlant(MultiWidget):

    def __init__(self, laboratory, servo):
        self._laboratory = laboratory
        self._actor = TentacleActor(laboratory, servo,
            state_to_angle_range= {
                STATE_PEACE: (30, 130),
                STATE_AGITATED: (30, 130),
                STATE_ATTACK: (30, 130)
            },
            state_to_speed_range= {
                STATE_PEACE: (0.05, 0.1),
                STATE_AGITATED: (0.1, 0.2),
                STATE_ATTACK: (0.1, 0.3),
            },
            state_to_pause_range= {
                STATE_PEACE: (0.1, 0.2),
                STATE_AGITATED: (0.1, 0.2),
                STATE_ATTACK: (0.1, 0.2),
            },
            initial = 80,
            min_move_angle = 30
        )
        servo.move_to(80, 0.5)
        MultiWidget.__init__(self, self._actor)


class Laborant(MultiWidget):
    # axe = 20
    # end of tentacles = 50
    # room = 100
    # tentacle_plant = 120
    # alert = 130
    # lab_corner = 140
    # computer = 180

    def __init__(self, laboratory, chair_servo):
        self._chair = TentacleActor(laboratory, chair_servo,

            state_to_angle_range= {
                STATE_PEACE: (140, 180),
                STATE_AGITATED: (100, 130),
                STATE_ATTACK: (20, 100)
            },
            state_to_speed_range= {
                STATE_PEACE: (0.1, 0.1),
                STATE_AGITATED: (0.1, 0.3),
                STATE_ATTACK: (0.1, 0.5),
            },
            state_to_pause_range= {
                STATE_PEACE: (1, 4),
                STATE_AGITATED: (0.5, 3),
                STATE_ATTACK: (0.5, 2),
            },
            initial=180
        )
        MultiWidget.__init__(self, self._chair)

    def look_at_alarm(self):
        self._chair.move_to(130, 0.3)

    def look_at_tentacle_plant(self):
        self._chair.move_to(115, 0.1)

    def look_at_breakout(self):
        self._chair.move_to(50, 0.5)




class Alarm(Widget):
    def __init__(self, led):
        Widget.__init__(self)
        self._led = led

    def _set_led_source(self, source):
        self._led.source = source

    def when_turn_off(self):
        self._led.source = AlwaysOff()

    def danger(self):
        (Script()
            .add_step(ecotron.siren.DEFAULT.danger)
            .add_sleep(0.5)
            .add_step(lambda: self._set_led_source(Sine(
                ecotron.siren.DANGER_CLIP_PULSE_LENGTH,
                source=Constant(0.5),
                common_phase=False
        )))
        ).execute()

    def warning(self):
        (Script()
            .add_step(ecotron.siren.DEFAULT.warning)
            .add_sleep(0.5)
            .add_step(lambda: self._set_led_source(Sine(
                ecotron.siren.WARNING_CLIP_PULSE_LENGTH,
                source=Constant(0.5),
                common_phase=False
        )))
        ).execute()

    def off(self):
        ecotron.siren.DEFAULT.off()
        self._led.source = self._led.source = AlwaysOff()


class Laboratory(MultiWidget):

    def __init__(self,
        stretch_servo,
        rotate_servo,
        uprighter_servo,
        chair_servo,
        stalk_servo,
        siren_led,
        top_light_pixels,
        stalker_light_pixels,
        tentacle_light_pixels,
        properties=DEFAULT_ECOTRON_PROPERTIES
        ):
        self._tentacle_plant = TentaclePlant(self, stretch_servo, rotate_servo, uprighter_servo)
        self._stalk_plant = StalkPlant(self, stalk_servo)
        self._laborant = Laborant(self, chair_servo)
        self._alarm = Alarm(siren_led)

        self._top_lights = Lights(top_light_pixels, properties.laboratory_top_lights_color)
        self._top_lights.bind_to_property(properties.laboratory_top_lights_on)
        self._stalker_lights = Lights(stalker_light_pixels, properties.laboratory_stalker_lights_color)
        self._stalker_lights.bind_to_property(properties.laboratory_stalker_lights_on)
        self._tentacle_lights = Lights(tentacle_light_pixels, properties.laboratory_tentacle_lights_color)
        self._tentacle_lights.bind_to_property(properties.laboratory_tentacle_lights_on)
        self._state = STATE_PEACE
        # TODO pass lights as well when not on own
        MultiWidget.__init__(self, self._tentacle_plant, self._stalk_plant, self._laborant, self._alarm)

    def toggle_attack(self):
        if not self._on:
            return
        if self._state == STATE_PEACE:
            print("AGITATED")
            self._state = STATE_AGITATED
            (Script()
                .add_step(lambda: say(SpeechLines.TENTACLE_PLANT_AGITATED))
                .add_sleep(2)
                .add_step(self._alarm.warning)
                .add_sleep(1)
                .add_step(self._laborant.look_at_alarm)
                .add_sleep(0.5)
                .add_step(self._laborant.look_at_tentacle_plant)
            ).execute()
        elif self._state == STATE_AGITATED:
            print("ATTACK")
            self._state = STATE_ATTACK
            self._tentacle_plant.breakout()
            (Script()
                .add_sleep(0.5)
                .add_step(self._alarm.danger)
                .add_step(lambda: say(SpeechLines.TENTACLE_PLANT_BREAKOUT))
                .add_step(self._laborant.look_at_breakout)

            ).execute()
        else:
            print("PEACE")
            self._state = STATE_PEACE
            self._tentacle_plant.peace()
            say(SpeechLines.TENTACLE_PLANT_PEACE)
            self._alarm.off()



