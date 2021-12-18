from ecotron import color_controller
import board
import value_source
from ecotron.lights import floor_lights
from value_source import RGB, AlwaysOff
from components.neopixels import NeopixelStrip, NeopixelSegment, Neopixels, NeopixelMultiSegment, FakeNeopixels
from tick_aware import DEFAULT_CONTROLLER
from director import Director
import time
from value_source import RGB
#from effects.electricity import zap

neopixels = NeopixelStrip(board.D21, 117)

np = NeopixelSegment(neopixels, 95, 10)

np.source = RGB(255, 255, 255)
DEFAULT_CONTROLLER.on = True

input()


np.source = AlwaysOff()
time.sleep(1)
