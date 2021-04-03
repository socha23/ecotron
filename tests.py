import os
from sound import Clip
from led_strip import strip_on, strip_off
from adafruit_servokit import ServoKit

import time


CLIP_DING = Clip("./resources/elevator_ding2.ogg")

kit = ServoKit(channels=16, reference_clock_speed=25000000)
kit.continuous_servo[0].set_pulse_width_range(1560, 2114)

strip_on()

kit.continuous_servo[0].throttle = 1
CLIP_DING.play()
time.sleep(5)
strip_off()
kit.continuous_servo[0].throttle = 0

