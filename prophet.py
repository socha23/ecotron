import os
import sound
import glob
import time
from random import randrange
from random_sequence import RandomSequence

from led_strip import strip_on

MAX_SOUNDS = sound.max_channels()
VOL_MAIN = 1
VOL_DROPOFF = 0.4

EVERY_SEC = 9

files = RandomSequence(glob.glob("../ecotron_resources/resources/audio/smac/tech*.ogg"))

stereos = RandomSequence([[1, 0], [0.7, 0.4], [0.6, 0.6], [0.4, 0.7], [0, 1]])
#stereos = [[0.5, 0], [0.4, 0.1], [0.3, 0.3], [0.1, 0.4], [0, 0.5]]

sounds = []

while True:
    if len(sounds) == MAX_SOUNDS:
        sounds.pop(0)
    for s in sounds:
        s.set_volume(s.get_volume() * VOL_DROPOFF)
    s = sound.play(files.next(), stereo=stereos.next(), volume=VOL_MAIN)
    sounds.append(s)

    strip_on((randrange(256), randrange(256), randrange(256)))

    input()
#    time.sleep(EVERY_SEC)

