from tick_aware import TimeAware
from director import Script
from value_source import AlwaysOff, repeated_pulse, Constant
from speech import SpeechLines, say
from sound import Clip

OPEN_SPEED = 0.3
CLOSE_SPEED = 0.3

RED_BLINKS_BRIGHTNESS = 1
RED_BLINKS_COUNT = 5
RED_BLINK_DURATION = 1

GREEN_BLINKS_BRIGHTNESS = 0.5
GREEN_BLINKS_COUNT = 2
GREEN_BLINK_DURATION = 0.2

DOOR_OPEN_DURATION = 3

AIRLOCK_PAUSE_DURATION = 2

AIRLOCK_SPEECH_VOLUME = 0.4

SAY_WELCOME_COMMANDER_AFTER = 5 * 60

CLIP_OPEN = Clip("./resources/airlock_open.ogg", )
CLIP_DOOR = Clip("./resources/servo_move.ogg", )
CLIP_FILL = Clip("./resources/airlock_fill.ogg", )

CLIP_WAIT = Clip("./resources/button_wait_05s.ogg", volume=0.5)
CLIP_SUCCESS = Clip("./resources/button_success_05s.ogg", volume=0.5)

class AirlockDoor:
    def __init__(self, name, red_led, green_led, door_servo, angle_closed, angle_open):
        self._red_led = red_led
        self._green_led = green_led
        self._door_servo = door_servo
        self._angle_closed = angle_closed
        self._angle_open = angle_open
        self._door_servo.angle = angle_closed

    def open_script(self):
        return (Script()
            .add_step(CLIP_OPEN.play)
            .add_sleep(0.3)
            .add_step(CLIP_DOOR.play)
            .add_sleep(0.2)
            .add_async_step(lambda c: self._door_servo.move_to(self._angle_open, OPEN_SPEED, c))
        )

    def close_script(self):
        return (Script()
            .add_step(CLIP_DOOR.play)
            .add_sleep(0.2)
            .add_async_step(lambda c: self._door_servo.move_to(self._angle_closed, CLOSE_SPEED, c))
        )

    def _play_fill_airlock(self, time=RED_BLINKS_COUNT * RED_BLINK_DURATION):
        c = CLIP_FILL
        (Script()
            .add_step(lambda: c.play(volume=0.4, fadein=1))
            .add_sleep(time - 1 - 0.2)
            .add_step(lambda: c.fadeout(2.5))
        ).execute()

    def cycle_script(self, speech_line=None):
        s = Script()
        if speech_line:
            s.add_step(lambda: say(speech_line))
        s.add_step(self._play_fill_airlock)
        for _ in range(RED_BLINKS_COUNT):
            s.add_step(lambda: self._red_led.set_source(repeated_pulse(1, RED_BLINK_DURATION, Constant(RED_BLINKS_BRIGHTNESS))))
            s.add_step(CLIP_WAIT.play)
            s.add_sleep(RED_BLINK_DURATION)

        s.add_step(lambda: self._red_led.set_source(AlwaysOff()))
        s.add_sleep(1)
        for _ in range(GREEN_BLINKS_COUNT):
            s.add_step(lambda: self._green_led.set_source(repeated_pulse(1, GREEN_BLINK_DURATION, Constant(GREEN_BLINKS_BRIGHTNESS))))
            s.add_step(CLIP_SUCCESS.play)
            s.add_sleep(GREEN_BLINK_DURATION)
            s.add_step(lambda: self._green_led.set_source(AlwaysOff()))
        return s

    def door_cycle_script(self, speech_line):
        return (self.cycle_script(speech_line)
            .add(self.open_script())
            .add_sleep(DOOR_OPEN_DURATION)
            .add(self.close_script())
        )


class Airlock(TimeAware):
    def __init__(self,
        inner_red, inner_green, inner_door_servo, inner_angle_closed, inner_angle_open,
        outer_red, outer_green, outer_door_servo, outer_angle_closed, outer_angle_open,
    ):
        TimeAware.__init__(self)
        self._inner_door = AirlockDoor("inner", inner_red, inner_green, inner_door_servo, inner_angle_closed, inner_angle_open)
        self._outer_door = AirlockDoor("outer", outer_red, outer_green, outer_door_servo, outer_angle_closed, outer_angle_open)
        self._during_cycle = False
        self._last_cycle_from_outside = 0


    def end_cycle(self):
      self._during_cycle = False

    def run_cycle_from_outside(self):
        if self._during_cycle:
          return
        self._during_cycle = True

        s = (Script()
            .add(self._outer_door.door_cycle_script(SpeechLines.DEPRESSURIZING_AIRLOCK))
            .add_sleep(AIRLOCK_PAUSE_DURATION)
            .add(self._inner_door.door_cycle_script(SpeechLines.PRESSURIZING_AIRLOCK))
        )

        if self.current_time() - self._last_cycle_from_outside > SAY_WELCOME_COMMANDER_AFTER:
            self._last_cycle_from_outside = self.current_time()
            s.add_step(lambda: say(SpeechLines.WELCOME_COMMANDER))

        s.add_step(self.end_cycle)
        s.execute()

    def run_cycle_from_inside(self):
        if self._during_cycle:
          return
        self._during_cycle = True

        (Script()
            .add(self._inner_door.door_cycle_script(SpeechLines.PRESSURIZING_AIRLOCK))
            .add_sleep(AIRLOCK_PAUSE_DURATION)
            .add(self._outer_door.door_cycle_script(SpeechLines.DEPRESSURIZING_AIRLOCK))
            .add_step(self.end_cycle)
        ).execute()
