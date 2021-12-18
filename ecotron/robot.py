from value_source import Lambda, Max, Min, ValueSource, EyeBlink, Multiply, Constant, FadeInOut, AlwaysOff, AlwaysOn
from .widget import PausingActor
from director import Script

class RobotHead(PausingActor):
    def __init__(self, eye_led, speech,
            standby_brightness = 0.2,
            total_brightness=1, volume=1,
            min_idle_time=5, max_idle_time=30,
            ):
        PausingActor.__init__(self, min_idle_time, max_idle_time)
        self._speech_flash_source = RobotSpeechEyeFlash(standby_brightness)
        self._eye_source = FadeInOut(duration_s=0.5, source=
            Multiply(
                Min(
                    Multiply(EyeBlink()),
                    self._speech_flash_source
                ), Constant(total_brightness)
            )
        )
        self._eye_led = eye_led
        self.restore_eye_source()
        self._volume = volume
        self._speech = speech
        self._current_sentence = None

    def restore_eye_source(self):
        self._eye_led.source = self._eye_source

    def set_eye_source(self, source):
        self._eye_led.source = source

    def speak(self, beep_sentence, callback=lambda:None):
        if self._current_sentence:
            self._current_sentence.stop()
            self._current_sentence = None
        self._current_sentence = beep_sentence
        (Script()
            .add_step(lambda: self._speech_flash_source.start_sentence(beep_sentence))
            .add_async_step(lambda c: beep_sentence.play(volume=self._volume, on_complete=c))
            .add_step(self._reset_current_sentence)
        ).execute(callback)

    def _reset_current_sentence(self):
        self._current_sentence = None

    def when_turn_on(self):
        self.force_action(lambda c: self.speak(self._speech.beeps_hello(), c))
        self._eye_source.fade_in()

    def when_turn_off(self):
        super().when_turn_off()
        self.restore_eye_source()
        self._eye_source.fade_out()
        self.speak(self._speech.beeps_bye())

    def say_yes(self, callback=lambda:None):
        self.speak(self._speech.beeps_yes(), callback)

    def say_no(self, callback=lambda:None):
        self.speak(self._speech.beeps_no(), callback)

    def say_angry(self, callback=lambda:None):
        self.speak(self._speech.beeps_angry(), callback)

    def _say_random(self, min_length=3, max_length=10, callback=lambda:None):
        self.speak(self._speech.beeps_random(min_length, max_length), callback)

    def do_action(self, callback):
        print(f"SAY RANDOM {self}")
        self._say_random(callback=callback)

FLASH_DELAY = 0.4

class RobotSpeechEyeFlash(ValueSource):
    def __init__(self, standby_brightness):
        ValueSource.__init__(self)
        self._sentence = None
        self._start_time = 0
        self._standby_brightness = standby_brightness

    def start_sentence(self, sentence):
        self._sentence = sentence
        self._start_time = self.current_time()

    def value(self):
        if self._sentence == None:
            return self._standby_brightness

        t = self.current_time() - self._start_time
        if t < FLASH_DELAY:
            return self._standby_brightness
        elif t > FLASH_DELAY + self._sentence.duration_s():
            self._sentence = None
            return self._standby_brightness
        else:
            (pitch, att) = self._sentence.pitch_and_att(t - FLASH_DELAY)
            pitch_mul = pitch
            att_mul = att**3
            return min(1, max(0, self._standby_brightness + (1 - self._standby_brightness) * pitch_mul * att_mul))
