import board
from busio import I2C, SPI
from digitalio import DigitalInOut
import value_source
from value_source import RGB
from components.neopixels import NeopixelStrip, NeopixelSegment
from tick_aware import DEFAULT_CONTROLLER
from director import Director
#import hyperscanner
import time

#from effects.electricity import zap

neopixels = NeopixelStrip(board.D21, 17)

director = Director()

#seg = NeopixelSegment(neopixels, 0, 1)
#seg2 = NeopixelSegment(neopixels, 1, 1)

neopixels.set(0, [(1, 1, 1)])
neopixels.set(1, [(1 , 0, 0)])
neopixels.set(2, [(0, 0.1, 0)])
neopixels.set(3, [(0, 0, 0.1)])
neopixels.set(4, [(0.1, 0, 0)])
neopixels.set(5, [(0, 0.1, 0)])
neopixels.set(6, [(0, 0, 0.1)])
neopixels.set(7, [(0.1, 0, 0)])
neopixels.set(8, [(0, 0.1, 0)])
neopixels.set(9, [(0, 0, 0.1)])
#NeopixelSegment(neopixels, 0, 1).source = value_source.RGB(16, 0, 0)
#NeopixelSegment(neopixels, 1, 1).source = value_source.RGB(0, 16, 0)
#hs = hyperscanner.Hyperscanner(inner, outer)

DEFAULT_CONTROLLER.on = True
#seg2.source = value_source.RGB(128, 0, 0)
input()
#hs.off()
#time.sleep(0.3)
#director.execute(hyperscanner.scan_cycle_script(hs, 10))
#while True:
    #zap(director, inner)
    #input()
#hs.off()
time.sleep(1)

