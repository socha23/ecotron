from ecotron import color_controller
import board
import value_source
from ecotron.lights import floor_lights
from value_source import RGB
from components.neopixels import NeopixelStrip, NeopixelSegment, Neopixels, NeopixelMultiSegment, FakeNeopixels
from tick_aware import DEFAULT_CONTROLLER
from director import Director
import time
from value_source import RGB
#from effects.electricity import zap

neopixels = NeopixelStrip(board.D21, 76)

np_tl_jungle = NeopixelSegment(neopixels, 0, 8) 
np_hyperscanner_outer = NeopixelSegment(neopixels, 9, 1)
np_hyperscanner_inner = NeopixelSegment(neopixels, 10, 1)
np_conveyor_receiver = NeopixelSegment(neopixels, 26, 1)
np_door = NeopixelSegment(neopixels, 39, 3)
np_tl_1 = NeopixelSegment(neopixels, 42, 22)
np_elevator = NeopixelSegment(neopixels, 64, 12)

np_fl_1_1 = Neopixels(neopixels, 8, 1)
np_fl_1_2 = Neopixels(neopixels, 11, 15)
np_fl_1_3 = Neopixels(neopixels, 27, 2)
np_fl_2_1 = Neopixels(neopixels, 29, 10)



np_tl_jungle.source = RGB(64, 0, 0)
np_hyperscanner_outer.source = RGB(0, 0, 64)
np_hyperscanner_inner.source = RGB(64, 0, 0)
np_conveyor_receiver.source = RGB(0, 0, 64)
np_door.source = RGB(0, 0, 64)
np_tl_1.source = RGB(64, 0, 0)
np_elevator.source = RGB(0, 0, 64)



lights = floor_lights(
                NeopixelMultiSegment(np_fl_1_1, FakeNeopixels(2), np_fl_1_2, FakeNeopixels(2), np_fl_1_3, np_fl_2_1),
                RGB(0, 64, 0),
                color_controller=color_controller.ColorController())



director = Director()
DEFAULT_CONTROLLER.on = True

lights.turn_on()

input()

lights.turn_off()

np_tl_jungle.off()
np_hyperscanner_outer.off()
np_hyperscanner_inner.off()
np_conveyor_receiver.off()
np_door.off()
np_tl_1.off()
np_elevator.off()

time.sleep(1)
