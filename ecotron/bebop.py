from beeper.robot_beeps import random_sentence
import random
from value_source import ValueSource, MultiplySource, ConstantSource

BLINK_TIME = 0.2
PAUSE_BETWEEN_BLINKS = 4

def random_pause_between_blinks():
    return PAUSE_BETWEEN_BLINKS * (random.random() + random.random())


class EyeBlink(ValueSource):
    def __init__(self):
        ValueSource.__init__(self)
        self._blink_start = self.current_time() + random_pause_between_blinks()

    def value(self):
        t = self.current_time()
        if t > self._blink_start and t < self._blink_start + BLINK_TIME:
            blink_phase = (t - self._blink_start) / BLINK_TIME
            brightness = abs(blink_phase - 0.5)
            return brightness
        elif t > self._blink_start + BLINK_TIME:
            self._blink_start = t + random_pause_between_blinks()
            return 1
        else: # t < self._blink_start
            return 1

STANDBY_EYE_BRIGHTNESS = 0.1
MAX_EYE_BRIGHTNESS = 0.8

FLASH_DELAY = 0.4

class EyeFlash(ValueSource):
    def __init__(self, sentence, on_complete):
        ValueSource.__init__(self)
        self._sentence = sentence
        self._start_time = self.current_time()
        self.on_complete = on_complete
        
    def value(self):
        t = self.current_time() - self._start_time
        if t < FLASH_DELAY:
            return STANDBY_EYE_BRIGHTNESS
        elif t > FLASH_DELAY + self._sentence.duration_s():
            self.on_complete()
            return STANDBY_EYE_BRIGHTNESS
        else:
            (pitch, att) = self._sentence.pitch_and_att(t - FLASH_DELAY)
            pitch_mul = pitch
            att_mul = att**3 
            return STANDBY_EYE_BRIGHTNESS + (MAX_EYE_BRIGHTNESS - STANDBY_EYE_BRIGHTNESS) * pitch_mul * att_mul

class Bebop:
    def __init__(self, servo, pwm_led):
        self._servo = servo
        self._eye = pwm_led
        self.standby()

    def speak(self):
        s = random_sentence()
        self._eye.source = EyeFlash(s, on_complete=self.standby)
        s.play()

    def standby(self):
        self._eye.source = MultiplySource(EyeBlink(), STANDBY_EYE_BRIGHTNESS)


    

