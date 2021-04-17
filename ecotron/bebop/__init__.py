from beeper.robot_beeps import random_sentence
import random
from value_source import ValueSource, MultiplySource
from director import Director, Script, ScriptQueue, script_with_step
from utils import translate
from ecotron.widget import Widget

class Bebop(Widget):

    def __init__(self, director, servo, pwm_led):
        Widget.__init__(self)
        self._servo = servo
        self._eye = pwm_led
        self._visible_plants = []
        self._last_sentence = None

    @property
    def angle(self):
        return self._servo.angle

    @angle.setter
    def angle(self, new_angle):
        self._servo.angle = new_angle

    def min_angle(self):
        return self._servo.min_angle

    def max_angle(self):
        return self._servo.max_angle


    def visible_plant_angle(self, idx=0):
        if self._visible_plants:
            return self._visible_plants[idx]
        else:
            return None

    def visible_plants(self):
        return self.visible_plants


    ####
    # behavior
    ####

    def when_plants_moved(self, positions):
        def plant_pos_to_angle(pos):
            if pos < 2.9:
                return None
            elif pos <= 3.7:
                return translate(pos, 2.9, 3.7, 0, 30)
            elif pos < 4.82:
                return translate(pos, 3.7, 4.82, 30, 60)
            elif pos < 5.84:
                return translate(pos, 4.82, 5.84, 60, 90)
            elif pos < 7:
                return translate(pos, 5.84, 7, 90, 120)
            elif pos < 7.75:
                return translate(pos, 7, 7.75, 120, 150)
            elif pos <= 9:
                return translate(pos, 7.75, 9, 150, 180)
            else:
                return None

        plants = []
        for p in positions:
            angle = plant_pos_to_angle(p)
            if angle:
                plants.append(angle)
        self._visible_plants = plants

    DEFAULT_VOLUME = 0.5

    def speak(self, sentence=random_sentence(), emotion=1, volume=DEFAULT_VOLUME):
        if self._last_sentence:
            self._last_sentence.stop()
        self._eye.source = EyeFlash(sentence, on_complete=self.standby, emotion=emotion)
        
        sentence.play(volume=volume)
        self._last_sentence = sentence

    def angry(self):
        pass

    def standby(self):
        self._eye.source = MultiplySource(EyeBlink(), STANDBY_EYE_BRIGHTNESS)


        
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
    def __init__(self, sentence, on_complete, emotion=1):
        ValueSource.__init__(self)
        self._sentence = sentence
        self._start_time = self.current_time()
        self.on_complete = on_complete
        self._emotion = emotion
        
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
            return min(1, max(0, STANDBY_EYE_BRIGHTNESS + (MAX_EYE_BRIGHTNESS - STANDBY_EYE_BRIGHTNESS) * pitch_mul * att_mul * self._emotion))        

