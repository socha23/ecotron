from adafruit_servokit import ServoKit
from time import sleep
from adafruit_pca9685 import PCA9685
import board

pca = PCA9685(board.I2C())
pca.frequency = 50

# 0x5000 = CLOCKWISE

#pca.channels[0].duty_cycle = 0x5500

# pca.channels[0].duty_cycle = 0x4000 clockwise fast

# pca.channels[0].duty_cycle = 0x1780 # zero

pca.channels[0].duty_cycle = 0xc000

sleep(2)

pca.channels[0].duty_cycle = 0x0000

#kit = ServoKit(channels=16, reference_clock_speed=25000000)

#NEUTRAL = 132

# nice settings for small servo running as 360:
#kit.continuous_servo[0].set_pulse_width_range(1560, 2114)

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
