import board
import value_source
from value_source import RGB
from components.neopixels import NeopixelStrip, NeopixelSegment
from tick_aware import DEFAULT_CONTROLLER
from director import Director
import time
from value_source import RGB
#from effects.electricity import zap

neopixels = NeopixelStrip(board.D21, 17)

director = Director()

outer = NeopixelSegment(neopixels, 0, 1)
outer.source = RGB(128, 0, 0)


inner = NeopixelSegment(neopixels, 1, 1)
inner.source = RGB(0, 128, 0)

DEFAULT_CONTROLLER.on = True
#director.execute(peaceful_screen_script(inner))
input()
inner.off()
outer.off()


