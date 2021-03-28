import board
from busio import I2C
from adafruit_mcp230xx.mcp23017 import MCP23017
from ecotron.elevator import Elevator, ElevatorControls


class Ecotron:
    def __init__(self, hub):
        print("INITIALIZING ECOTRON")
        self.hub = hub
        self.mcp1 = MCP23017(I2C(board.SCL, board.SDA), address=0x20)
        self.elevatorControls = ElevatorControls(self.mcp1)
        self.elevator = Elevator(hub.device("A"), self.elevatorControls)    