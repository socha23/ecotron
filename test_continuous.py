from adafruit_servokit import ServoKit
from time import sleep
from adafruit_pca9685 import PCA9685
import board
import random
from components.led import PWMLED
from tick_aware import DEFAULT_CONTROLLER, TickAware
from value_source import ValueSource, Multiply, Constant
from components.servo import Servo

#pca = PCA9685(board.I2C())
#pca.frequency = 50

# 0x5000 = CLOCKWISE

#pca.channels[0].duty_cycle = 0x5500

# pca.channels[0].duty_cycle = 0x4000 clockwise fast

# pca.channels[0].duty_cycle = 0x1780 # zero

#pca.channels[0].duty_cycle = 0x5000


#pca.channels[0].duty_cycle = 0x0000


kit = ServoKit(channels=16, address=0x40)

s = kit.continuous_servo[1]
#s.set_pulse_width_range(1450, 2200) # first, non-converted 1370

#s.set_pulse_width_range(830, 2250) # second, converted 1370 (1370-2)
s.set_pulse_width_range(870, 2250) # third, converted 1370 (1370-3)

# mid point: 1820

s.throttle = -1
input()
s.throttle = -0.5
input()
s.throttle = -0.1
input()
s.throttle = 0.1
input()
s.throttle = 0.5
input()
s.throttle = 1
input()
s.throttle = 0
input()


#s = kit.servo[1]
#s.angle = 0
#input()
#s.angle = 180
#input()

#servo = kit.servo[15]
#servo = Servo(kit.servo[12])

#DEFAULT_CONTROLLER.on = True

#angle = 0
#while True:
#  print(f"angle: {angle}")
#  input()
#  angle += 30
#  if angle > 180:
#    angle = 0
#  servo.move_to(angle, 0.4, lambda: print("X"))
#  sleep(1)

