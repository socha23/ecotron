import time

from beeper.synthesis2 import triangle, square, adsr, make_clip

t = 1
f = 440

sound = (triangle(f, t) * 0.7 + square(f, t) * 0.3) * adsr(t, 0.1, 0.2, 0.5, 0.2, 1, 0.5) * 0.2
make_clip(sound).play()

time.sleep(1)
