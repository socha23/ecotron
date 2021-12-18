from tick_aware import TimeAware
from director import Script, script_with_step, script_with_async_step
from value_source import AlwaysOff, repeated_pulse, Constant
from beeper.beeps2 import airlock_speech
from speech import SpeechLines, say

OPEN_SPEED = 0.2
CLOSE_SPEED = 0.2

RED_BLINKS_BRIGHTNESS = 1
RED_BLINKS_COUNT = 3
RED_BLINK_DURATION = 1

GREEN_BLINKS_BRIGHTNESS = 0.5
GREEN_BLINKS_COUNT = 2
GREEN_BLINK_DURATION = 0.2

DOOR_OPEN_DURATION = 5

AIRLOCK_PAUSE_DURATION = 2

SPEECH = airlock_speech()
AIRLOCK_SPEECH_VOLUME = 0.4

SENTENCE_OK = SPEECH.create_sentence(
    SPEECH.beep_by_idx(1, 1),
    SPEECH.beep_by_idx(3, 1),
)

SAY_WELCOME_COMMANDER_AFTER = 5 * 60

class AirlockDoor:
    def __init__(self, name, red_led, green_led, door_servo, angle_closed, angle_open):
        self._red_led = red_led
        self._green_led = green_led
        self._door_servo = door_servo
        self._angle_closed = angle_closed
        self._angle_open = angle_open
        self._door_servo.angle = angle_closed

    def open_script(self):
        return script_with_async_step(lambda c: self._door_servo.move_to(self._angle_open, OPEN_SPEED, c))

    def close_script(self):
        return script_with_async_step(lambda c: self._door_servo.move_to(self._angle_closed, CLOSE_SPEED, c))

    def cycle_script(self, speech_line=None):
        s = Script().add_step(lambda: self._red_led.set_source(repeated_pulse(RED_BLINKS_COUNT, RED_BLINK_DURATION, source=Constant(RED_BLINKS_BRIGHTNESS))))
        if speech_line:
            s.add_step(lambda: say(speech_line))
        return (s
            .add_sleep(RED_BLINKS_COUNT * RED_BLINK_DURATION)
            .add_step(lambda: self._red_led.set_source(AlwaysOff()))
            .add_step(lambda: SENTENCE_OK.play(volume=AIRLOCK_SPEECH_VOLUME))
            .add_sleep(0.4)
            .add_step(lambda: self._green_led.set_source(repeated_pulse(GREEN_BLINKS_COUNT, GREEN_BLINK_DURATION, source=Constant(GREEN_BLINKS_BRIGHTNESS))))
            .add_sleep(GREEN_BLINKS_COUNT * GREEN_BLINK_DURATION)
            .add_step(lambda: self._green_led.set_source(AlwaysOff()))
        )

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
