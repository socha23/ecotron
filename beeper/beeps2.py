from beeper.synthesis import make_sample, make_clip, Sawtooth, Sine, Multiply, Const, Clip, Triangle, Square, ADSR, Add
import beeper.synthesis2 as bs
import random
import logging
import time

SCALE_JUST = [1, 9/8, 5/4, 4/3, 3/2, 5/3, 15/8]
SCALE_PYTHAGOREAN = [1, 9/8, 81/64, 4/3, 3/2, 27/16, 243/128]
SCALE_PENTATONIC = [1, 6/5, 4/3, 3/2, 9/5]

LOGGER = logging.getLogger("RobotBeeps")


def octave_up(scale):
    return [x * 2 for x in scale]

def octave_down(scale):
    return [x / 2 for x in scale]

#DEFAULT_SCALE = SCALE_PENTATONIC + octave_up(SCALE_PENTATONIC)
DEFAULT_SCALE = SCALE_JUST
DEFAULT_LENGTHS_AND_WEIGHTS = [ # short beeps more likely than long ones
    (0.1,  4),
    (0.2, 2),
    (0.4, 1),
]

class Phonemes:
    def __init__(self, pitches_count = len(DEFAULT_SCALE), lengths_and_weights = DEFAULT_LENGTHS_AND_WEIGHTS):
        self._pitches_count = pitches_count
        self._lengths_and_weights = lengths_and_weights

        self._weighted_lengths = []
        self._lengths = []
        for (length, weight) in lengths_and_weights:
            self._lengths.append(length)
            for _ in range(weight):
                self._weighted_lengths.append(length)

    def pitches_count(self):
        return self._pitches_count

    def lengths(self):
        return self._lengths

    def length_short(self):
        return self._lengths[0]

    def length_long(self):
        return self._lengths[-1]


    # random phoneme - returns a pair of (pitch idx, length)

    def random(self):
        return (self._random_pitch(), self._random_length())

    def random_high_fast(self):
        return (self._random_pitch_high(), self._random_length_fast())

    def _random_length(self):
        return random.choice(self._weighted_lengths)

    def _random_length_fast(self):
        return min(self._random_length(), self._random_length())

    def _random_pitch(self):
        return random.randrange(0, self.pitches_count())

    def _random_pitch_high(self):
        return max(self._random_pitch(), self._random_pitch(), self._random_pitch())

DEFUALT_PHONEMES = Phonemes()


class Language:
    def __init__(self, phonemes = DEFUALT_PHONEMES):
        self._phonemes = phonemes

        self._yes = [self.random_sentence(4, 10) for _ in range(4)]
        self._no = [self.random_sentence(4, 10) for _ in range(4)]
        self._angry = [self.random_angry_sentence(5, 15) for _ in range(3)]

    # sentence is a list of pairs of (pitch idx, length)

    def random_sentence(self, min_len = 2, max_len = 10):
        return [self._phonemes.random() for _ in range(random.randrange(min_len, max_len))]

    def random_angry_sentence(self, min_len = 2, max_len = 10):
        return [self._phonemes.random_high_fast() for _ in range(random.randrange(min_len, max_len))]

    def random_yes(self):
        return random.choice(self._yes)

    def random_no(self):
        return random.choice(self._no)

    def random_angry(self):
        return random.choice(self._angry)

    def hello(self):
        return [
            (2, self._phonemes.length_short()),
            (5, self._phonemes.length_long()),
        ]

    def bye(self):
        return [
            (5, self._phonemes.length_short()),
            (2, self._phonemes.length_long()),
        ]


DEFAULT_LANGUAGE = Language()

ADSR_RATIOS = [0.1, 0.2, 0.5, 0.2]
ADSR_ATT = [1, 0.7]

DEFAULT_ADSR = [*ADSR_RATIOS, *ADSR_ATT]

class Beep:
    def __init__(self, sound, envelope, pitch, duration_s):
        self.sound = sound
        self.envelope = envelope
        self.pitch = pitch
        self.duration_s = duration_s

def silence(duration_s):
    return Beep(bs.silence(duration_s), bs.silence(duration_s), 0, duration_s)


class RobotVoice:

    # waveform generator is a closure that takes pitch idx and length, and generates a waveform

    def __init__(self, waveform_generator, phonemes = DEFUALT_PHONEMES, name = "Robot beeps", adsr_def=DEFAULT_ADSR):
        library_generation_start = time.time()
        self._phonemes = phonemes
        self._name = name
        self._beeps = {}
        for length in phonemes.lengths():
            adsr = bs.adsr(length, *adsr_def)
            for pitch_idx in range(phonemes.pitches_count()):
                sound = waveform_generator(pitch_idx, length) * adsr
                beep = Beep(sound, adsr, (pitch_idx + 1) / phonemes.pitches_count(), length)
                self._beeps[(pitch_idx, length)] = beep
        LOGGER.info(f"Beeps library {self._name} generated in {time.time() - library_generation_start}")

    def beep(self, word):
        return self._beeps[word]

    def beep_by_idx(self, pitch_idx=0, length_idx=0):
        if pitch_idx < 0:
            pitch_idx += self._phonemes.pitches_count()
        length = self._phonemes.lengths()[length_idx]
        return self.beep((pitch_idx, length))


class BeepSentence:
    def __init__(self, beeps, stereo=None):
        self.beeps = beeps
        self.clip = bs.make_clip(*[b.sound for b in self.beeps], stereo)

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


class RobotSpeech:
    def __init__(self, generator, name = "Robot speech", phonemes = DEFUALT_PHONEMES, language = DEFAULT_LANGUAGE, stereo = None):
        self._language = language
        self._stereo = stereo
        self._phonemes = phonemes
        self._voice = RobotVoice(generator, phonemes, name)

    def _sentence_to_beeps(self, sentence):
        return BeepSentence([self._voice.beep(word) for word in sentence], self._stereo)

    def beeps_yes(self):
        return self._sentence_to_beeps(self._language.random_yes())

    def beeps_no(self):
        return self._sentence_to_beeps(self._language.random_no())

    def beeps_angry(self):
        return self._sentence_to_beeps(self._language.random_angry())

    def beeps_hello(self):
        return self._sentence_to_beeps(self._language.hello())

    def beeps_bye(self):
        return self._sentence_to_beeps(self._language.bye())


    def beeps_random(self, min_length=3, max_length=10):
        return self._sentence_to_beeps(self._language.random_sentence(min_length, max_length))

    def beep_by_idx(self, pitch_idx=0, length_idx=0):
        return self._voice.beep_by_idx(pitch_idx, length_idx)

    def create_sentence(self, *beeps):
        return BeepSentence(beeps, self._stereo)



def quick_robot_speech(name="Robot speech", base_freq=300, triangle_coefficient = 0, square_coefficient = 0, sawtooth_coefficient = 0, sine_coefficient = 0, scale = DEFAULT_SCALE, stereo=None):
    if not stereo:
        stereo = (0.5, 0.5)

    return RobotSpeech(
        lambda freq_idx, length:  (
            bs.triangle(scale[freq_idx] * base_freq, length) * triangle_coefficient +
            bs.square(scale[freq_idx] * base_freq, length) * square_coefficient +
            bs.sawtooth(scale[freq_idx] * base_freq, length) * sawtooth_coefficient +
            bs.sine(scale[freq_idx] * base_freq, length) * sine_coefficient

            ),
        name,
        stereo=stereo
    )


def airlock_speech():
    return quick_robot_speech("airlock", 300, sine_coefficient=1, stereo=(0.4, 0.6))

def bebop_speech():
    return quick_robot_speech("bebop", 300, triangle_coefficient=0.8, square_coefficient=0.2, stereo=(0.5, 0.5))

def eddard_speech():
    return quick_robot_speech("eddard", 80,
        triangle_coefficient=0,
        square_coefficient=0,
        sawtooth_coefficient=0.8,
        sine_coefficient=0.2,
        stereo=(0.6, 0.4)

    )

def spiderbro_speech():
    return quick_robot_speech("spiderbro", 40,
        triangle_coefficient=0,
        square_coefficient=0.5,
        sawtooth_coefficient=0.5,
        sine_coefficient=0,
        stereo=(1, 0)

    )

