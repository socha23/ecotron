from adafruit_servokit import ServoKit
from time import sleep
from adafruit_pca9685 import PCA9685
import board
import random
from components.led import PWMLED
from tick_aware import DEFAULT_CONTROLLER, TickAware
from value_source import ValueSource, Multiply, Constant
from components.servo import Servo


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

# reactor kit3, servo 15 (tentacles-stretch):
# min_range = 600
# max_range = 2900
# tentacle_hidden = 140
# tentacle_action = 100
# tentacle_all_out = 0

# reactor kit3, servo 14 (tentacles-rotate):
# min_range = 600
# max_range = 2900
# tentacle_max_fold = 140
# tentacle_straight = 110
# tentacle_all_out = 60

# reactor kit3, servo 13 (uprighter):
# min_range = 700
# max_range = 2900
# neutral = 20
# closed = 120

# reactor kit3, servo 12 (chair):
# min_range = 700
# max_range = 2900
# axe = 20
# end of tentacles = 50
# room = 100
# tentacle_plant = 120
# alert = 130
# lab_corner = 140
# computer = 180

# reactor kit3, servo 7 (stalkplant):
# min_range = 700
# max_range = 2900
# min = 20
# max = 140

#kit = ServoKit(channels=16, address=0x40)
#kit = ServoKit(channels=16, address=0x41)
kit = ServoKit(channels=16, address=0x42)
s = kit.servo[7]

min_range = 700
max_range = 2900


s.set_pulse_width_range(min_range, max_range)
angle = 20

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
   angle += 10
   input()

#s.set_pulse_width_range(1450, 2200) # first, non-converted 1370

#s.set_pulse_width_range(830, 2250) # second, converted 1370 (1370-2)
#s.set_pulse_width_range(870, 2250) # third, converted 1370 (1370-3)

