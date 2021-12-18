from ecotron.airlock import Airlock
from ecotron.conveyor import ConveyorControls
from adafruit_servokit import ServoKit
from time import sleep
from adafruit_pca9685 import PCA9685
import board
import random
from components.led import PWMLED
from tick_aware import DEFAULT_CONTROLLER, TickAware
from value_source import ValueSource, Multiply, Constant, Sine, AlwaysOff
from components.servo import Servo
from components.buffering_mcp23017 import BufferingMcp23017
from busio import I2C, SPI
from digitalio import DigitalInOut
from adafruit_mcp3xxx.mcp3008 import MCP3008
from director import Director

spi = SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = DigitalInOut(board.D5)
mcp3008a = MCP3008(spi, cs)
mcp23017a_1 = BufferingMcp23017(I2C(board.SCL, board.SDA), address=0x20)
controls = ConveyorControls(mcp23017a_1, mcp3008a)
kit = ServoKit(channels=16, address=0x40)

DEFAULT_CONTROLLER.on = True

airlock = Airlock(Director(), 
  inner_red=PWMLED(kit._pca.channels[10]), inner_green=PWMLED(kit._pca.channels[9]), inner_door_servo=Servo(kit.servo[11]), inner_angle_closed=180, inner_angle_open=90,
  outer_red=PWMLED(kit._pca.channels[7]), outer_green=PWMLED(kit._pca.channels[6]), outer_door_servo=Servo(kit.servo[8]), outer_angle_closed=0, outer_angle_open=90,  
)

controls.button_blue.on_click = lambda _: airlock.run_cycle_from_outside()
controls.button_yellow.on_click = lambda _: airlock.run_cycle_from_inside()

input()