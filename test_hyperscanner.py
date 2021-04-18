import board
from busio import I2C, SPI
from digitalio import DigitalInOut
from adafruit_servokit import ServoKit
import value_source
from value_source import RGB
from components.neopixels import NeopixelStrip, NeopixelSegment
from tick_aware import DEFAULT_CONTROLLER
from director import Director
import hyperscanner
import time
neopixels = NeopixelStrip(board.D21, 17)

director = Director()

hs = hyperscanner.Hyperscanner(NeopixelSegment(neopixels, 0, 1), NeopixelSegment(neopixels, 1, 1))

DEFAULT_CONTROLLER.on = True
hs.off()
time.sleep(0.3)
director.execute(hyperscanner.scan_cycle_script(hs, 10))

hs.run_gradient([
    (0, RGB(0, 0, 0)),
    (0.2, RGB(255, 0, 0)),
    (0.4, RGB(0, 255, 0)),
    (0.6, RGB(0, 0, 255)),
    (1, RGB(0, 0, 0)),
])

input()
hs.off()
time.sleep(1)

