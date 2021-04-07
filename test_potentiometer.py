import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP

from tick_aware import DEFAULT_CONTROLLER

from components.potentiometer import Potentiometer

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)

pot = Potentiometer(mcp, MCP.P0)

pot.on_change = lambda x: print(f"Val: {x}")

DEFAULT_CONTROLLER.on = True

input()
