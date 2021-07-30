from adafruit_servokit import ServoKit
from time import sleep
from adafruit_pca9685 import PCA9685
import board
import random
from components.led import PWMLED
from tick_aware import DEFAULT_CONTROLLER
from value_source import ValueSource, Multiply, Constant

#pca = PCA9685(board.I2C())
#pca.frequency = 50

# 0x5000 = CLOCKWISE

#pca.channels[0].duty_cycle = 0x5500

# pca.channels[0].duty_cycle = 0x4000 clockwise fast

# pca.channels[0].duty_cycle = 0x1780 # zero

#pca.channels[0].duty_cycle = 0x5000


#pca.channels[0].duty_cycle = 0x0000

BLINK_TIME = 0.2
PAUSE_BETWEEN_BLINKS = 4

def random_pause_between_blinks():
    return PAUSE_BETWEEN_BLINKS * (random.random() + random.random())

class EyeBlink(ValueSource):
    def __init__(self):
        ValueSource.__init__(self)
        self._blink_start = 0

    def value(self):
        t = self.current_time()
        if t > self._blink_start and t < self._blink_start + BLINK_TIME:
            blink_phase = (t - self._blink_start) / BLINK_TIME
            brightness = abs(blink_phase - 0.5)
            return brightness
        elif t > self._blink_start + BLINK_TIME:
            self._blink_start = t + random_pause_between_blinks()
            return 1
        else: # t < self._blink_start
            return 1

kit_a = ServoKit(channels=16, address=0x40)
servo_stairs = kit_a.servo[12]

kit_b = ServoKit(channels=16, address=0x41)

servo_spider = kit_b.servo[0]
spider_eye = PWMLED(kit_b._pca.channels[1])
spider_eye.source = Multiply(EyeBlink(), Constant(0.1))


eyes_1 = PWMLED(kit_b._pca.channels[2])
eyes_2 = PWMLED(kit_b._pca.channels[3])
eyes_3 = PWMLED(kit_b._pca.channels[4])
eyes_4 = PWMLED(kit_b._pca.channels[5])
eyes_5 = PWMLED(kit_b._pca.channels[6])

eyes_1.source = Multiply(EyeBlink(), Constant(0.15))
eyes_2.source = Multiply(EyeBlink(), Constant(0.15))
eyes_3.source = Multiply(EyeBlink(), Constant(0.15))
eyes_4.source = Multiply(EyeBlink(), Constant(0.15))
eyes_5.source = Multiply(EyeBlink(), Constant(0.15))



angle = 0

DEFAULT_CONTROLLER.on = True

while True:
  new_angle = angle
  while abs(new_angle - angle) < 20:
    new_angle = random.randrange(180)
  angle = new_angle
  #servo_stairs.angle = angle
  servo_spider.angle = angle
  print(f"Setting angle {angle}")
  sleep(1)
  servo_stairs.angle = None
  servo_spider.angle = None
  input()


#NEUTRAL = 132


#kit.continuous_servo[0].throttle = 1

#sleep(5)

#kit.continuous_servo[0].throttle = 0

# nice settings for small servo running as 360:
#

# my micro servo as a continuous servo:
#kit.continuous_servo[0].set_pulse_width_range(1515, 2150)


#kit.servo[0].angle = 10

#for i in range(10):
  #kit.servo[0].angle = 180
  #sleep(1)
  #kit.servo[0].angle = None
  #sleep(1)


#kit.servo[0].angle = None

#kit.continuous_servo[1].throttle = 0

#kit.servo[1].angle = 90
#sleep(2)
#kit.continuous_servo[1].throttle = 0.5

#sleep(2)

#kit.continuous_servo[1].throttle = 0

#kit.servo[1].angle = None
