import board
from busio import I2C, SPI
from digitalio import DigitalInOut
from adafruit_mcp230xx.mcp23017 import MCP23017
from adafruit_mcp3xxx.mcp3008 import MCP3008
from adafruit_servokit import ServoKit
import logging

import value_source
from director import Director
from ecotron.conveyor import Conveyor, ConveyorControls
from ecotron.elevator import Elevator, ElevatorControls
from ecotron.fans import Fans
from ecotron.bebop import Bebop
from ecotron.hyperscanner import Hyperscanner
from ecotron.properties import EcotronProperties
from components.toggle import Toggle, ToggleBoard
from components.servo import Servo
from components.led import PWMLED
from components.neopixels import NeopixelStrip, NeopixelSegment
from speech import say, SpeechLines
from tick_aware import DEFAULT_CONTROLLER
from ecotron.scripts import Scripter
from speech import say, SpeechLines
from sound import set_master_volume

logger = logging.getLogger(__name__)

class Ecotron:
    def __init__(self, hub):
        logger.info("*** Ecotron startup ***")
        hub.wait_for_devices("A", "B", "C", "D")


        mcp23017a_1 = MCP23017(I2C(board.SCL, board.SDA), address=0x20)
        mcp23017a_2 = MCP23017(I2C(board.SCL, board.SDA), address=0x21)
        spi = SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        cs = DigitalInOut(board.D5)
        mcp3008a = MCP3008(spi, cs)
        servo_kit = ServoKit(channels=16, reference_clock_speed=25000000)
        neopixels = NeopixelStrip(board.D21, 29)

        controls = EcotronControls(mcp23017a_1, mcp23017a_2, mcp3008a)
        properties = EcotronProperties()

        bind_controls_to_properties(controls, properties)

        director = Director()
        base = EcotronBase(hub, servo_kit, neopixels, controls, director, properties)
        master_controller = MasterController(base)

        scripter = Scripter(director, base, controls, master_controller)

        bind_properties_to_components(properties, base)
        bind_controls_to_actions(controls, base, master_controller, scripter)
        
        base.floor_light.source = value_source.Multiply(
            value_source.Wave(15, pixels_per_s=10, inner_source=value_source.RGB(0, 32, 0)),
            properties.light_strip_on
        )
        
        DEFAULT_CONTROLLER.on = True

        say(SpeechLines.ECOTRON_READY)
        logger.info("*** Ecotron startup complete ***")

class EcotronControls:
    def __init__(self, mcp23017a_1, mcp23017a_2, mcp3008a):
        self.elevator_controls = ElevatorControls(mcp23017a_1)
        self.conveyor_controls = ConveyorControls(mcp23017a_1, mcp3008a)
        self.toggle_board = ToggleBoard([Toggle(mcp23017a_2.get_pin(idx)) for idx in range(10)])


class EcotronBase:
    def __init__(self, hub, servo_kit, neopixels, controls, director, ecotron_properties):
            self.floor_light = NeopixelSegment(neopixels, 2, 15)
            self.elevator = Elevator(director, controls.elevator_controls, hub.device("A"), NeopixelSegment(neopixels, 17, 12), ecotron_properties)

            self.conveyor = Conveyor(hub.device("D"), controls.conveyor_controls, director)
            self.bebop = Bebop(director, Servo(servo_kit.servo[13]), PWMLED(servo_kit._pca.channels[14]))
            self.hyperscanner = Hyperscanner(NeopixelSegment(neopixels, 1, 1), NeopixelSegment(neopixels, 0, 1))
            self.fans = Fans(hub.device("C"))


class MasterController:
    def __init__(self, base):
        self._base = base
        self._calibration = False
        self.metatron_on = True

    @property
    def calibration(self):
        return self._calibration

    @calibration.setter
    def calibration(self, val):
        if self._calibration == val:
            return
        self._calibration = val
        if val:
            self.enter_calibration()
        else:
            self.exit_calibration()
        
    def enter_calibration(self):
        self._metatron(SpeechLines.CONVEYOR_CALIBRATION_STARTED)
        pass

    def exit_calibration(self):
        self._base.conveyor.reset_position()
        self._metatron(SpeechLines.CONVEYOR_CALIBRATION_COMPLETE)

    def _metatron(self, speech_line):
        if not self.metatron_on:
            return
        say(speech_line)



def bind_elevator(elevator, elevator_controls):
        for floor_idx in range(len(Elevator.FLOOR_HEIGHTS)):
            elevator_controls.floor_buttons[floor_idx].on_press = lambda floor_idx=floor_idx: elevator.go_to_floor(floor_idx)                   
        elevator_controls.button_red.on_press = elevator.go_floor_up
        elevator_controls.button_green.on_press = elevator.go_floor_down
                    

def bind_conveyor_controls(conveyor_controls, master_controller, base, scripter):

    def red_pressed():
        base.bebop.angry()

    def blue_pressed():
        if master_controller.calibration:
            base.conveyor.calibration_backward()
        else:
            base.bebop.angle -= 30

    def green_pressed():
        if master_controller.calibration:
            base.conveyor.calibration_forward()
        else:
            base.bebop.angle += 30


    def yellow_pressed():
        master_controller.calibration = not master_controller.calibration

    conveyor_controls.button_yellow.on_press = yellow_pressed
    conveyor_controls.button_green.on_press = green_pressed
    conveyor_controls.button_blue.on_press = blue_pressed
    conveyor_controls.button_red.on_press = red_pressed

    conveyor_controls.master_switch.on_press = scripter.production_line.production_line_on
    conveyor_controls.master_switch.on_release = scripter.production_line.production_line_off
    if conveyor_controls.master_switch.is_pressed():
        scripter.production_line.production_line_on()


def bind_controls_to_properties(controls, properties):
    
    controls.toggle_board.toggles[0].bind_property(properties.master_volume)
    controls.toggle_board.toggles[1].bind_property(properties.light_strip_on)
    controls.toggle_board.toggles[2].bind_property(properties.fans_on)
    controls.toggle_board.toggles[3].bind_property(properties.elevator_lights_on)

def bind_properties_to_components(properties, base):
    properties.master_volume.on_value_change = lambda x : set_master_volume(x)
    base.fans.bind_to_property(properties.fans_on)

def bind_controls_to_actions(controls, base, master_controller, scripter):
    bind_elevator(base.elevator, controls.elevator_controls)
    bind_conveyor_controls(controls.conveyor_controls, master_controller, base, scripter)

