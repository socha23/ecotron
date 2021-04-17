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
from ecotron.bebop import Bebop
from components.servo import Servo
from components.led import PWMLED
from components.neopixels import NeopixelStrip, NeopixelSegment
from speech import say, SpeechLines
from tick_aware import DEFAULT_CONTROLLER

logger = logging.getLogger(__name__)

class Ecotron:
    def __init__(self, hub):
        logger.info("*** Ecotron startup ***")
        hub.wait_for_devices("A", "B", "D")

        director = Director()

        mcp23017a = MCP23017(I2C(board.SCL, board.SDA), address=0x20)
        spi = SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        cs = DigitalInOut(board.D5)
        mcp3008a = MCP3008(spi, cs)
        servo_kit = ServoKit(channels=16, reference_clock_speed=25000000)
        neopixels = NeopixelStrip(board.D21, 17)

        elevator_controls = ElevatorControls(mcp23017a)
        conveyor_controls = ConveyorControls(mcp23017a, mcp3008a)

        base = EcotronBase(hub, servo_kit, neopixels, elevator_controls, conveyor_controls, director)

        bind_controls(base, elevator_controls, conveyor_controls)


        
        #base.floor_light.source = value_source.Wave(15, pixels_per_s=10, inner_source=value_source.ConstantSource((0, 0.2, 0)))

        #base.machine_inner.source = value_source.Blink([0.1, 1])
        #base.machine_outer.source = value_source.ConstantSource((0.1, 0, 0))

        #base.bebop.on = True
        #base.conveyor.on = True

        DEFAULT_CONTROLLER.on = True

        #say(SpeechLines.ECOTRON_READY)
        logger.info("*** Ecotron startup complete ***")

class EcotronBase:
    def __init__(self, hub, servo_kit, neopixels, elevator_controls, conveyor_controls, director):
            self.floor_light = NeopixelSegment(neopixels, 2, 15)
            self.elevator = Elevator(director, elevator_controls, hub.device("A"))    
            self.conveyor = Conveyor(hub.device("D"), conveyor_controls, director)
            self.bebop = Bebop(director, Servo(servo_kit.servo[13]), PWMLED(servo_kit._pca.channels[14]))

            self.machine_inner = NeopixelSegment(neopixels, 0, 1)
            self.machine_outer = NeopixelSegment(neopixels, 1, 1)

            self.bebop.angle = 90


def bind_elevator(elevator, elevator_controls):
        for floor_idx in range(len(Elevator.FLOOR_HEIGHTS)):
            elevator_controls.floor_buttons[floor_idx].on_press = lambda floor_idx=floor_idx: elevator.go_to_floor(floor_idx)                   
        elevator_controls.button_red.on_press = elevator.go_floor_up
        elevator_controls.button_green.on_press = elevator.go_floor_down
                    

def bind_conveyor(conveyor_controls, conveyor, bebop):

    bebop.observe(conveyor)

    def red_pressed():
        bebop.angry()

    def blue_pressed():
        if conveyor.is_calibrating():
            conveyor.calibration_backward()
        else:
            bebop.angle -= 30

    def green_pressed():
        if conveyor.is_calibrating():
            conveyor.calibration_forward()
        else:
            bebop.angle += 30


    def yellow_pressed():
        if not conveyor.is_calibrating():
            conveyor.enter_calibration()
        else:
            conveyor.finish_calibration()

    conveyor_controls.button_yellow.on_press = yellow_pressed
    conveyor_controls.button_green.on_press = green_pressed
    conveyor_controls.button_blue.on_press = blue_pressed
    conveyor_controls.button_red.on_press = red_pressed


def bind_controls(base, elevator_controls, conveyor_controls):
    bind_elevator(base.elevator, elevator_controls)
    bind_conveyor(conveyor_controls, base.conveyor, base.bebop)
