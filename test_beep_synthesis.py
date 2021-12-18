import time

from beeper.beeps2 import airlock_speech, silence



b = airlock_speech()

b.create_sentence(
    b.beep_by_idx(5, 1),
    b.beep_by_idx(5, 1),
    b.beep_by_idx(5, 1),
).play()

input()
