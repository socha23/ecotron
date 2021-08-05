import board
from adafruit_mcp230xx.mcp23017 import MCP23017
from busio import I2C, SPI

from components.encoder import Encoder
from components.color_dials import ColorDials

from time import sleep
from tick_aware import DEFAULT_CONTROLLER

mcp23017a_3 = MCP23017(I2C(board.SCL, board.SDA), address=0x22)

color_dials = ColorDials(
    Encoder(mcp23017a_3.get_pin(1), mcp23017a_3.get_pin(0)),
    Encoder(mcp23017a_3.get_pin(3), mcp23017a_3.get_pin(2)),
    Encoder(mcp23017a_3.get_pin(5), mcp23017a_3.get_pin(4)),
    Encoder(mcp23017a_3.get_pin(7), mcp23017a_3.get_pin(6)),
    Encoder(mcp23017a_3.get_pin(8), mcp23017a_3.get_pin(9))
    )

color_dials.on_change_red = lambda s: print(f"red: {s}")
color_dials.on_change_green = lambda s: print(f"green: {s}")
color_dials.on_change_blue = lambda s: print(f"blue: {s}")
color_dials.on_change_x1 = lambda s: print(f"x1: {s}")
color_dials.on_change_x2 = lambda s: print(f"x2: {s}")

DEFAULT_CONTROLLER.on = True

input()
