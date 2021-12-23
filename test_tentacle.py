from adafruit_servokit import ServoKit
from time import sleep
from adafruit_pca9685 import PCA9685
import board
import random
from components.led import PWMLED
from director import DEFAULT_DIRECTOR
from tick_aware import DEFAULT_CONTROLLER, TickAware
from value_source import ValueSource, Multiply, Constant
from components.servo import Servo
from ecotron.tentacle_plant import TentaclePlant

kit = ServoKit(channels=16, address=0x42)

tp = TentaclePlant(
    stretch_servo=Servo(kit.servo[15], angle=140, min_pulse_witdh_range=600, max_pulse_witdh_range=2900),
    rotate_servo=Servo(kit.servo[14], angle=110, min_pulse_witdh_range=600, max_pulse_witdh_range=2900),
    uprighter_servo=Servo(kit.servo[13], angle=20, min_pulse_witdh_range=700, max_pulse_witdh_range=2900)
)

DEFAULT_CONTROLLER.on = True
tp.turn_on()

print("ready...")
while True:
    input()
    print("breakout!")
    tp.breakout()
    input()
    print("peace...")
    tp.peace()


