from beeper.synthesis import make_sample, make_clip, Sawtooth, Sine, Multiply, Const, Clip, Triangle, Square, ADSR, Add
import beeper.synthesis2 as bs
from random import randrange, choice, randint
import logging
import time

SCALE_JUST = [1, 9/8, 5/4, 4/3, 3/2, 5/3, 15/8]
SCALE_PYTHAGOREAN = [1, 9/8, 81/64, 4/3, 3/2, 27/16, 243/128]
SCALE_PENTATONIC = [1, 6/5, 4/3, 3/2, 9/5]

def octave_up(scale):
    return [x * 2 for x in scale]

def octave_down(scale):
    return [x / 2 for x in scale]

def scale_frequencies(scale, base):
    return [base * x for x in scale]

DEFAULT_SCALE = SCALE_PENTATONIC + octave_up(SCALE_PENTATONIC)
DEFAULT_LENGTHS_AND_WEIGHTS = [ # short beeps more likely than long ones
    (0.1,  4),
    (0.20, 2),
    (0.4, 1),
]

ADSR_RATIOS = [0.1, 0.2, 0.5, 0.2]
ADSR_ATT = [1, 0.7]

DEFAULT_ADSR = [*ADSR_RATIOS, *ADSR_ATT]

class Beep:
    def __init__(self, sound, envelope, pitch, duration_s):
        self.sound = sound
        self.envelope = envelope
        self.pitch = pitch
        self.duration_s = duration_s

class BeepLibrary:
    def __init__(self, base_freq, name="Beeps library", scale=DEFAULT_SCALE, lengths_and_weights = DEFAULT_LENGTHS_AND_WEIGHTS, adsr_def=DEFAULT_ADSR):
        self._logger = logging.getLogger("RobotBeeps")
        self._beeps = []
        self._name = name
        self._weighted_beeps = []
        self._generate_beeps(base_freq, scale, lengths_and_weights, adsr_def)

    def _generate_beeps(self, base_freq, scale, lengths_and_weights, adsr_def):
        frequencies = scale_frequencies(scale, base_freq)
        library_generation_start = time.time()
        for (length, weight) in lengths_and_weights:
            beeps_of_length = []
            adsr = bs.adsr(length, *adsr_def)
            for (pitch_idx, freq) in enumerate(frequencies):
                sound  = (bs.triangle(freq, length) * 0.8 + bs.square(freq, length) * 0.2) * adsr * 0.2
                beep = Beep(sound, adsr, (pitch_idx + 1) / len(frequencies), length)
                beeps_of_length.append(beep)
            self._beeps.append(beeps_of_length)
            for _ in range(weight):
                self._weighted_beeps.append(beeps_of_length)
        self._logger.info(f"Beeps library {self._name} generated in {time.time() - library_generation_start}")

    def random_beep(self):
        row = choice(self._weighted_beeps) 
        val_idx = int((randrange(len(row)) + randrange(len(row))) / 2) # poor man's gauss
        return row[val_idx]


class BeepSentence:
    def __init__(self, beeps):
        self.beeps = beeps
        self.clip = bs.make_clip(*[b.sound for b in self.beeps])

    def play(self, volume=1, on_complete=lambda:None):
        self.clip.volume = volume
        self.clip.play(on_complete=on_complete)

    def stop(self):
        self.clip.stop()

    def duration_s(self):
        return sum([b.duration_s for b in self.beeps])
    
    def pitch_and_att(self, time_s):
        for b in self.beeps:
            if time_s < b.duration_s:
                return (b.pitch, b.envelope[int(time_s * bs.SAMPLE_RATE)])
            time_s -= b.duration_s
        return (0, 0)
    
    def pitch(self, time_s):
        return self.pitch_and_att(time_s)[0]

    def att(self, time_s):
        return self.pitch_and_att(time_s)[1]

VOICE_BEBOP = BeepLibrary(300, "bebob")

def random_sentence(min_len=2, max_len=10, voice=VOICE_BEBOP):
    length = randint(min_len, max_len)
    beeps = []
    for _ in range(length):
        beeps.append(voice.random_beep())
    return BeepSentence(beeps)


def random_sentence_of_duration(duration=3, voice=VOICE_BEBOP):
    beeps = []
    duration_left = duration
    while duration_left > 0:
        next_beep = voice.random_beep()
        duration_left -= next_beep.duration_s
        beeps.append(next_beep)
    return BeepSentence(beeps)

