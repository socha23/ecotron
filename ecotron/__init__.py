import board
from busio import I2C
from adafruit_mcp230xx.mcp23017 import MCP23017
import logging

import value_source
from director import Director
from ecotron.elevator import Elevator, ElevatorControls
from components.neopixels import NeopixelStrip, NeopixelSegment

from tick_aware import DEFAULT_CONTROLLER

logger = logging.getLogger(__name__)

class Ecotron:
    def __init__(self, hub):
        logger.info("*** Ecotron startup ***")
        hub.wait_for_devices("A", "B", "D")
        self.hub = hub
        self.director = Director()

        self.mcp1 = MCP23017(I2C(board.SCL, board.SDA), address=0x20)
        self.neopixels = NeopixelStrip(board.D21, 15)

        self.elevatorControls = ElevatorControls(self.mcp1)
        self.elevator = Elevator(hub.device("A"), self.elevatorControls, self.director)    

        self.floor_light = NeopixelSegment(self.neopixels, 0, 15)

        
        self.floor_light.source = value_source.Wave(15, pixels_per_s=10, inner_source=value_source.ConstantSource((0, 32, 0)))
        
#        self.floor_light.source = value_source.Pulse(2, value_source.ConstantSource((0, 16, 0)))
#        self.floor_light.source = value_source.ConstantSource((0, 32, 0))


        DEFAULT_CONTROLLER.on = True

        logger.info("*** Ecotron startup complete ***")