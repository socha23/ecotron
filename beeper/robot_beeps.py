from beeper.synthesis import make_sample, make_clip, Sawtooth, Sine, Multiply, Const, Clip, Triangle, Square, ADSR, Add
from random import randrange, choice

SCALE_JUST = [1, 9/8, 5/4, 4/3, 3/2, 5/3, 15/8]
SCALE_PYTHAGOREAN = [1, 9/8, 81/64, 4/3, 3/2, 27/16, 243/128]
SCALE_PENTATONIC = [1, 6/5, 4/3, 3/2, 9/5]

def octave_up(scale):
    return [x * 2 for x in scale]

def octave_down(scale):
    return [x / 2 for x in scale]

SCALE_PENTATONIC_EXTENDED = SCALE_PENTATONIC + octave_up(SCALE_PENTATONIC)

def scale_frequencies(scale, base):
    return [base * x for x in scale]

FREQUENCIES = scale_frequencies(SCALE_PENTATONIC_EXTENDED, 300)

ADSR_RATIOS = [0.1, 0.2, 0.5, 0.2]
ADSR_ATT = [1, 0.7]

LENGTHS_AND_WEIGHTS = [ # short beeps more likely than long ones
    (0.1,  12),
    (0.15, 4),
    (0.17, 2),
    (0.20, 2),
    (0.3, 1),
    (0.4, 1),
]

class Beep:
    def __init__(self, sample, envelope, pitch, duration_s):
        self.sample = sample
        self.envelope = envelope
        self.pitch = pitch
        self.duration_s = duration_s
        
BEEPS = []
WEIGHTED_BEEPS = []
for (length, weight) in LENGTHS_AND_WEIGHTS:
    beeps_of_length = []
    adsr = ADSR(*[r * length for r in ADSR_RATIOS], *ADSR_ATT)
    for (pitch_idx, freq) in enumerate(FREQUENCIES):
        generator = Multiply(
            0.2,
            Add(
                Multiply(0.8, Triangle(freq)),
                Multiply(0.2, Square(freq)),
            ),
            adsr
        )
        sample = make_sample(length, generator)
        beep = Beep(sample, adsr, (pitch_idx + 1) / len(FREQUENCIES), length)
        beeps_of_length.append(beep)
    BEEPS.append(beeps_of_length)
    for _ in range(weight):
        WEIGHTED_BEEPS.append(beeps_of_length)


def random_beep(library=WEIGHTED_BEEPS):
    row = choice(library) 
    val_idx = int((randrange(len(row)) + randrange(len(row))) / 2) # poor man's gauss
    return row[val_idx]

class BeepSentence:
    def __init__(self, beeps):
        self.beeps = beeps
        self.clip = make_clip(*[b.sample for b in self.beeps])

    def play(self, on_complete=lambda:None):
        self.clip.play(on_complete=on_complete)

    def duration_s(self):
        return sum([b.duration_s for b in self.beeps])
    
    def pitch_and_att(self, time_s):
        for b in self.beeps:
            if time_s < b.duration_s:
                return (b.pitch, b.envelope[time_s])
            time_s -= b.duration_s
        return (0, 0)
    
    def pitch(self, time_s):
        return self.pitch_and_att(time_s)[0]

    def att(self, time_s):
        return self.pitch_and_att(time_s)[1]


def random_sentence():
    length = 2 + randrange(6) + randrange(6)
    beeps = []
    for _ in range(length):
        beeps.append(random_beep())
    return BeepSentence(beeps)

