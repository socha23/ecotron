import board
from busio import I2C
from adafruit_mcp230xx.mcp23017 import MCP23017
import logging

from director import Director
from ecotron.elevator import Elevator, ElevatorControls
from tick_aware import DEFAULT_CONTROLLER

logger = logging.getLogger(__name__)

class Ecotron:
    def __init__(self, hub):
        logger.info("*** Ecotron startup ***")
        hub.wait_for_devices("A", "B", "D")
        self.hub = hub
        self.director = Director()

        self.mcp1 = MCP23017(I2C(board.SCL, board.SDA), address=0x20)

        self.elevatorControls = ElevatorControls(self.mcp1)
        self.elevator = Elevator(hub.device("A"), self.elevatorControls, self.director)    

        DEFAULT_CONTROLLER.on = True

        logger.info("*** Ecotron startup complete ***")