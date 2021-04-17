from beeper.robot_beeps import random_sentence
import random
from value_source import ValueSource, MultiplySource, ConstantSource, AlwaysOffSource
from director import Director, Script, ScriptQueue, script_with_step
from utils import translate
from ecotron.widget import Widget

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

class Bebop(Widget):

    def __init__(self, director, servo, pwm_led):
        Widget.__init__(self)
        self._servo = servo
        self._eye = pwm_led
        self._visible_plants = []
        self._behavior = BebopBehavior(self, director)
        self._last_sentence = None

    def when_turn_on(self):
        self.standby()
        self._behavior.enqueue_idle_action()

    def when_turn_off(self):
        self._eye.source = AlwaysOffSource()

    def observe(self, conveyor):
        self._behavior.observe(conveyor)

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


    ####
    # behavior
    ####

    def when_plants_moved(self, phase, positions):
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
        if phase == 0:
            self._behavior.when_conveoyor_stops()


    DEFAULT_VOLUME = 0.5

    def speak(self, sentence=random_sentence(), emotion=1, volume=DEFAULT_VOLUME):
        if self._last_sentence:
            self._last_sentence.stop()
        self._eye.source = EyeFlash(sentence, on_complete=self.standby, emotion=emotion)
        
        sentence.play(volume=volume)
        self._last_sentence = sentence

    def angry(self):
        self._behavior.angry()

    def standby(self):
        self._eye.source = MultiplySource(EyeBlink(), STANDBY_EYE_BRIGHTNESS)


        
def rand_time(mean_s):
    return (random.random() + random.random()) * mean_s

class BebopBehavior:

    def __init__(self, bebop, director):
        self.bebop = bebop
        self._script_queue = ScriptQueue(director, self._when_script_queue_complete)        
        self._conveyor = None

        self._analysis_queued = False
        self._angry_queued = False

    def observe(self, conveyor):
        self._conveyor = conveyor
        conveyor.on_plants_moved = self.bebop.when_plants_moved

    def _when_script_queue_complete(self):
        if not self.bebop.on:
            return
        self.enqueue_idle_action()
        

    def _with_optional_chatter(self, script, chatter_prob = 0.3):
        if random.random() < chatter_prob:
            sentence = random_sentence(3, 10)
            if self._conveyor and (not self._conveyor.prognosed_time_to_finish_move() or self._conveyor.prognosed_time_to_finish_move() - sentence.duration_s()):
                return script.add_step_at_start(self.bebop.speak)        
        return script

    def _random_idle_script(self):
        
        if not self._conveyor:
            return self._with_optional_chatter(script_with_step(self._rotate_randomly), 1)

        if self._conveyor.prognosed_time_to_finish_move():
            if self._conveyor.prognosed_time_to_finish_move() > 2:
                r = random.random()
                if r < 0.4:
                    return self._with_optional_chatter(self._track_first_script())
                else:
                    return self._with_optional_chatter(self._track_last_script())
        
        if (not self._conveyor.prognosed_time_to_finish_move() or self._conveyor.prognosed_time_to_finish_move() > 0.7) and random.random() < 0.2:
                return self._with_optional_chatter(script_with_step(self._rotate_randomly))

        return Script().add_sleep(0.1)
            
    def _look_and_speak_script(self, angle=90):
        return script_with_step(lambda: self._rotate(angle)).add_step(self.bebop.speak)
        
    def _track_first_script(self):
        return self._tracking_script(0)

    def _track_last_script(self):
        return self._tracking_script(-1)

    def _rotate_randomly(self):        
        self._rotate(random.randrange(self.bebop.min_angle(), self.bebop.max_angle()))

    def _rotate(self, angle):        
        self.bebop.angle = angle

    def _rotate_to_visible(self, idx=0, twitch=0):        
        if self.bebop.visible_plant_angle(idx):
            self._rotate(self.bebop.visible_plant_angle(idx))


    SENTENCE_COMMENCING_SHORT_1 = random_sentence(2, 3)
    SENTENCE_COMMENCING_SHORT_2 = random_sentence(3, 4)
    SENTENCE_COMMENCING_MID_1 = random_sentence(3, 5)
     
    SENTENCE_OK_SHORT_1 = random_sentence(2, 3)
    SENTENCE_OK_SHORT_2 = random_sentence(2, 4)
    SENTENCE_OK_MID_1 = random_sentence(4, 5)
    SENTENCE_OK_MID_2 = random_sentence(4, 6)
    SENTENCE_OK_LONG_1 = random_sentence(7, 12)

    SENTENCES_COMMENCING = [SENTENCE_COMMENCING_SHORT_1, SENTENCE_COMMENCING_SHORT_2, SENTENCE_COMMENCING_MID_1]
    SENTENCES_OK = [SENTENCE_OK_SHORT_1, SENTENCE_OK_SHORT_1, SENTENCE_OK_SHORT_2, SENTENCE_OK_SHORT_2, SENTENCE_OK_MID_1, SENTENCE_OK_MID_2, SENTENCE_OK_LONG_1]

    def _angry_script(self):
        s = Script()
        curse = random_sentence(3, 12)
        PLAYER_POSITION = 70
        s.add_step(lambda:self._rotate(PLAYER_POSITION))
        s.add_step(lambda:self.bebop.speak(curse, emotion=2, volume=0.65))

        ANGER_STEP = 0.9
        ANGER_TWITCH_RANGE = 30

        for _ in range(int(curse.duration_s() / ANGER_STEP)):
            s.add_step(lambda: self._rotate(PLAYER_POSITION + random.randint(-ANGER_TWITCH_RANGE, ANGER_TWITCH_RANGE)))
            s.add_sleep(ANGER_STEP)
        s.add_sleep(1)
        return s

    def _analyze_plant_script(self):

        angle = self.bebop.visible_plant_angle(0)
        s = script_with_step(lambda: self._rotate(angle))

        was_enough_time = True

        s.add_sleep(0.5)
        time_left = max(0, 0 if not self._conveyor.prognosed_time_to_finish_pause() else self._conveyor.prognosed_time_to_finish_pause() - 0.5)
        if not time_left:
            was_enough_time = False
        else:
            sentence_commencing = random.choice(BebopBehavior.SENTENCES_COMMENCING)
            s.add_step(lambda: self.bebop.speak(sentence_commencing))
            s.add_sleep(sentence_commencing.duration_s())
            time_left -= sentence_commencing.duration_s()

            r = random.random()
            time_needed_for_analysis = 0
            if r < 0.7: # easy case
                time_needed_for_analysis = 1 + 2 * random.random()
            elif r < 0.9: # mid case
                time_needed_for_analysis = 2 + 2 * random.random()
            else: # hard case
                time_needed_for_analysis = 4 + 2 * random.random()

            was_enough_time = time_needed_for_analysis < time_left
            time_for_analysis = min(time_needed_for_analysis, time_left)
            time_left -= time_for_analysis

            ANALYSIS_STEP = 0.5
            ANALYSIS_TWITCH_RANGE = 20

            for _ in range(int(time_for_analysis / ANALYSIS_STEP)):
                s.add_step(lambda: self._rotate(angle + random.randint(-ANALYSIS_TWITCH_RANGE, ANALYSIS_TWITCH_RANGE)))
                s.add_sleep(ANALYSIS_STEP)

        if not was_enough_time:
            print("angry")
            s.add(self._angry_script())
        else:
            sentence_ok = random.choice(BebopBehavior.SENTENCES_OK)
            s.add_step(lambda: self.bebop.speak(sentence_ok))
            s.add_sleep(sentence_ok.duration_s() + 1)
        s.add_step(self._when_analysis_done)
        return s

    def _when_analysis_done(self):
        self._analysis_queued = False


    def _tracking_script(self, idx):
        MIN_LENGTH = 1
        MAX_LENGTH = self._conveyor.prognosed_time_to_finish_move() - 0.5

        track_length = random.uniform(MIN_LENGTH, MAX_LENGTH)
        
        PAUSE_BETWEEN_STEPS = 0.1

        s = Script()
        steps = int(track_length / PAUSE_BETWEEN_STEPS)
        for _ in range(steps):
            (s
                .add_step(lambda: self._rotate_to_visible(idx))
                .add_sleep(PAUSE_BETWEEN_STEPS)
            )
        return s

    def enqueue_idle_action(self):        
        self._script_queue.enqueue(self._random_idle_script())
        MEAN_PAUSE = 1 # todo
        PAUSE_STEP = 0.2
        for i in range(int(rand_time(MEAN_PAUSE) / PAUSE_STEP)):
            self._script_queue.enqueue(Script().add_sleep(PAUSE_STEP))


    def when_conveoyor_stops(self):
        if not self.bebop.on:
            return
        if self._analysis_queued:
            return
        self._analysis_queued = True
        self._script_queue.replace_queue(self._analyze_plant_script())

    def angry(self):
        self._script_queue.replace_queue(self._angry_script())
        

