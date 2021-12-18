from adafruit_servokit import ServoKit
from time import sleep
from adafruit_pca9685 import PCA9685
import board
import random
from components.led import PWMLED
from tick_aware import DEFAULT_CONTROLLER, TickAware
from value_source import ValueSource, Multiply, Constant
from components.servo import Servo

#kit = ServoKit(channels=16, address=0x40)
#kit = ServoKit(channels=16, address=0x41)
kit = ServoKit(channels=16, address=0x42)


s = kit.servo[11]

# bebop kit1, servo 13:
# min_range = 700
# max_range = 2650

# stairs kit1, servo 12:
# min_range = 700
# max_range = 2650

# spider kit2, servo 0:
# min_range = 700
# max_range = 2900

# reactor kit3, servo 11:
# min_range = 700
# max_range = 2900


min_range = 700
max_range = 2900


s.set_pulse_width_range(min_range, max_range)
angle = 90

#135 = closed

#while True:
#    print(f"setting minrange {min_range}")
#    s.set_pulse_width_range(min_range, max_range)
#    s.angle = 0
#    input()
#    min_range -= 50

#while True:
#    print(f"setting maxrange {max_range}")
#    s.set_pulse_width_range(min_range, max_range)
#    s.angle = 180
#    input()
#    max_range += 50

while True:
    print(f"setting angle {angle}")
    s.angle = angle
    angle -= 5
    input()

#s.set_pulse_width_range(1450, 2200) # first, non-converted 1370

#s.set_pulse_width_range(830, 2250) # second, converted 1370 (1370-2)
#s.set_pulse_width_range(870, 2250) # third, converted 1370 (1370-3)

