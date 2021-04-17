import board
from busio import I2C, SPI
from digitalio import DigitalInOut
from adafruit_servokit import ServoKit
import value_source
from components.neopixels import NeopixelStrip, NeopixelSegment
from tick_aware import DEFAULT_CONTROLLER
from director import Director
import hyperscanner
import time
neopixels = NeopixelStrip(board.D21, 17)

#hyperscanner_inner.source = value_source.Blink([0.1, 1])
#hyperscanner_outer.source = value_source.ConstantSource((0.1, 0, 0))

director = Director()

hs = hyperscanner.Hyperscanner(NeopixelSegment(neopixels, 0, 1), NeopixelSegment(neopixels, 1, 1))

DEFAULT_CONTROLLER.on = True
hs.off()
time.sleep(0.3)
director.execute(hyperscanner.scan_cycle_script(hs, 10))

input()
hs.off()
time.sleep(1)

