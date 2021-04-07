import board
from busio import I2C, SPI
from adafruit_mcp230xx.mcp23017 import MCP23017
from adafruit_mcp3xxx.mcp3008 import MCP3008
from adafruit_servokit import ServoKit
from time import sleep

from digitalio import DigitalInOut

import logging
import random

from ecotron.conveyor import ConveyorControls

from tick_aware import DEFAULT_CONTROLLER

mcp23017 = MCP23017(I2C(board.SCL, board.SDA), address=0x20)

spi = SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = DigitalInOut(board.D5)

mcp3008 = MCP3008(spi, cs)

kit = ServoKit(channels=16, reference_clock_speed=25000000)
kit.continuous_servo[0].set_pulse_width_range(1560, 2114)

servo_chair = kit.servo[15]

servo_robot = kit.servo[13]
light_robot = kit._pca.channels[14]

light_robot.duty_cycle = 0xffff

controls = ConveyorControls(mcp23017, mcp3008)


def test_robot(_):
    servo_robot.angle = random.randrange(20, 160)
    light_robot.duty_cycle = 0xffff
    sleep(0.5)
    light_robot.duty_cycle = 0x0000

def test_chair(_):
    servo_chair.angle = random.randrange(20, 160)



controls.button_blue.on_click = test_robot
controls.button_green.on_click = test_chair


DEFAULT_CONTROLLER.on = True


input()