from director import Script
from ecotron.bebop.language import random_sentence_commencing, random_sentence_ok
from beeper.robot_beeps import random_sentence, random_sentence_of_duration
import random

def _rotate_to_visible(bebop, idx=0, twitch=0):        
    angle = 0
    if bebop.visible_plant_angle(idx):
       angle = bebop.visible_plant_angle(idx)
    _rotate(bebop, angle, twitch)


def _rotate(bebop, angle, twitch=0):        
    new_angle = angle + random.randint(-twitch, twitch)
    bebop.angle = new_angle

def _twitch(bebop, range=20):        
    new_angle = bebop.angle + random.randint(-range, range)
    bebop.angle = new_angle

def _rotate_randomly(bebop, min_rotation=0):        
    new_angle = bebop.angle
    while abs(bebop.angle - new_angle) < min_rotation:
        new_angle = random.randrange(0, 180)
    bebop.angle = new_angle

def analyze_plant(bebop, max_duration=5):
    BEFORE_COMMENCING_TIME = 0.5
    sentence_commencing = random_sentence_commencing()
    
    s = (Script()
        .add_step(lambda: _rotate_to_visible(bebop,0))
        .add_sleep(BEFORE_COMMENCING_TIME)
        .add_step(lambda: bebop.speak(sentence_commencing))
        .add_sleep(sentence_commencing.duration_s())
    )

    time_left = max_duration - BEFORE_COMMENCING_TIME - sentence_commencing.duration_s()

    ANALYSIS_STEP = 0.5
    ANALYSIS_TWITCH_RANGE = 20

    SLEEP_AFTER_ANALYSIS = 0.5

    time_for_scanning = max(0, random.random() * (time_left - 1 - SLEEP_AFTER_ANALYSIS) + 1)
    for _ in range(int(time_for_scanning / ANALYSIS_STEP)):
        s.add_step(lambda: _rotate_to_visible(bebop, 0, ANALYSIS_TWITCH_RANGE))
        s.add_sleep(ANALYSIS_STEP)
    s.add_step(lambda: bebop.speak(random_sentence_ok()))
    s.add_sleep(SLEEP_AFTER_ANALYSIS)    
    return s



def trace_first_visible_plant(bebop, duration=5):
    PAUSE_BETWEEN_STEPS = 0.1    
    s = Script()
    for _ in range(int(duration / PAUSE_BETWEEN_STEPS)):
        s.add_step(lambda: _rotate_to_visible(bebop, 0))
        s.add_sleep(PAUSE_BETWEEN_STEPS)
    return s


def angry(bebop, duration=5):
    pass    
#    s = Script()
#    curse = random_sentence(3, 12)
#    PLAYER_POSITION = 70
#    s.add_step(lambda:self._rotate(PLAYER_POSITION))
#    s.add_step(lambda:self.bebop.speak(curse, emotion=2, volume=0.65))

#    ANGER_STEP = 0.9
#    ANGER_TWITCH_RANGE = 30

#    for _ in range(int(curse.duration_s() / ANGER_STEP)):
#        s.add_step(lambda: self._rotate(PLAYER_POSITION + random.randint(-ANGER_TWITCH_RANGE, ANGER_TWITCH_RANGE)))
#        s.add_sleep(ANGER_STEP)
#    s.add_sleep(1)
#    return s



def idle(bebop, duration=5):

    s = Script().add_step(lambda: bebop.standby())
    time_left = duration
    
    while time_left > 0:

        if duration < 0.2:
            return s
                    
        PAUSE_AFTER_MOVE = 0.5

        max_chatter_duration = min(time_left, 2)

        action_choice = random.randrange(100)
        if action_choice < 50 and time_left > 2.5:
            # trace for 2 < time_left seconds < 5
            trace_duration = _rand_duration(2, min(5, time_left - PAUSE_AFTER_MOVE))
            _add_optional_chatter(s, bebop, max_duration=max_chatter_duration)
            s.add(trace_first_visible_plant(bebop, trace_duration))
            time_left -= trace_duration
        elif action_choice < 60:
            # rotate in random direction
            _add_optional_chatter(s, bebop, max_duration=max_chatter_duration)
            s.add_step(lambda: _rotate_randomly(bebop, min_rotation = 50))
        else:
            s.add_step(lambda: _twitch(bebop, 20))
        s.add_sleep(PAUSE_AFTER_MOVE)
        time_left -= PAUSE_AFTER_MOVE
    return s

def _rand_duration(min, max):
    return random.uniform(min, max)

def _add_optional_chatter(script, bebop, min_duration=0.3, max_duration=2, chatter_prob = 0.3):
    if random.random() < chatter_prob:
        sentence = random_sentence_of_duration(random.uniform(min_duration, max_duration))
        script.add_step(lambda: bebop.speak(sentence))
