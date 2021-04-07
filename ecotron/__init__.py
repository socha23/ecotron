import board
from busio import I2C, SPI
from digitalio import DigitalInOut
from adafruit_mcp230xx.mcp23017 import MCP23017
from adafruit_mcp3xxx.mcp3008 import MCP3008
from adafruit_servokit import ServoKit
import logging

import value_source
from director import Director
from ecotron.conveyor import Conveyor, ConveyorControls
from ecotron.elevator import Elevator, ElevatorControls
from ecotron.bebop import Bebop
from components.led import PWMLED
from components.neopixels import NeopixelStrip, NeopixelSegment
from speech import say, SpeechLines
from tick_aware import DEFAULT_CONTROLLER

logger = logging.getLogger(__name__)

class Ecotron:
    def __init__(self, hub):
        logger.info("*** Ecotron startup ***")
        hub.wait_for_devices("A", "B", "D")
        self.hub = hub
        self.director = Director()

        self.mcp23017a = MCP23017(I2C(board.SCL, board.SDA), address=0x20)
        self.spi = SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        cs = DigitalInOut(board.D5)
        self.mcp3008a = MCP3008(self.spi, cs)
        self.servo_kit = ServoKit(channels=16, reference_clock_speed=25000000)
        self.neopixels = NeopixelStrip(board.D21, 15)

        self.floor_light = NeopixelSegment(self.neopixels, 0, 15)
        self.elevatorControls = ElevatorControls(self.mcp23017a)
        self.elevator = Elevator(hub.device("A"), self.elevatorControls, self.director)    
        self.conveyorControls = ConveyorControls(self.mcp23017a, self.mcp3008a)
        self.conveyor = Conveyor(hub.device("D"), self.conveyorControls, self.director)
        self.bebop = Bebop(self.servo_kit.servo[13], PWMLED(self.servo_kit._pca.channels[14]))

        self.conveyorControls.button_red.on_click = lambda _: self.bebop.speak()        
        
        self.floor_light.source = value_source.Wave(15, pixels_per_s=10, inner_source=value_source.ConstantSource((0, 32, 0)))

        DEFAULT_CONTROLLER.on = True

        say(SpeechLines.ECOTRON_READY)
        logger.info("*** Ecotron startup complete ***")
