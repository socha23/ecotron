from ecotron.color_controller import ColorController
from ecotron.conveyor_receiver import ConveyorReceiver
import board
from busio import I2C, SPI
from digitalio import DigitalInOut
from components.buffering_mcp23017 import BufferingMcp23017
from adafruit_mcp3xxx.mcp3008 import MCP3008
from adafruit_mcp230xx.mcp23017 import MCP23017
from adafruit_servokit import ServoKit
import logging

from director import Director
from ecotron.conveyor import Conveyor, ConveyorControls
from ecotron.elevator import Elevator, ElevatorControls
from ecotron.repair_table import RepairTable
from ecotron.fans import Fans
from ecotron.bebop import Bebop
from ecotron.hyperscanner import Hyperscanner
from ecotron.properties import EcotronProperties
from components.toggle import Toggle, ToggleBoard
from components.encoder import Encoder
from components.servo import Servo
from components.led import PWMLED
from components.neopixels import NeopixelStrip, NeopixelSegment, NeopixelMultiSegment, FakeNeopixels, Neopixels
from components.color_dials import ColorDials
from speech import say, SpeechLines
from tick_aware import DEFAULT_CONTROLLER
from ecotron.scripts import Scripter
from speech import say, SpeechLines
from sound import set_master_volume
from ecotron.lights import Lights, floor_lights
from ecotron.jungle import Jungle

logger = logging.getLogger(__name__)

class Ecotron:
    def __init__(self, hub):
        logger.info("*** Ecotron startup ***")
        hub.wait_for_devices("A", "B", "C", "D")


        #mcp23017a_1 = MCP23017(I2C(board.SCL, board.SDA), address=0x20)
        mcp23017a_1 = BufferingMcp23017(I2C(board.SCL, board.SDA), address=0x20)
        mcp23017a_2 = BufferingMcp23017(I2C(board.SCL, board.SDA), address=0x21)
        mcp23017a_3 = BufferingMcp23017(I2C(board.SCL, board.SDA), address=0x22)
        spi = SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        cs = DigitalInOut(board.D5)
        mcp3008a = MCP3008(spi, cs)
        servo_kit_1 = ServoKit(channels=16, reference_clock_speed=25000000)
        servo_kit_2 = ServoKit(channels=16, address=0x41)
        
        neopixels = NeopixelStrip(board.D21, 76)

        controls = EcotronControls(mcp23017a_1, mcp23017a_2, mcp23017a_3, mcp3008a)
        properties = EcotronProperties()
        
        color_controller = ColorController()

        controls.color_dials.bind(color_controller)


        bind_controls_to_properties(controls, properties)

        director = Director()
        base = EcotronBase(hub, servo_kit_1, servo_kit_2, neopixels, controls, director, properties, color_controller)
        master_controller = MasterController(base)

        scripter = Scripter(director, base, controls, master_controller)

        bind_controls_to_actions(controls, base, master_controller, scripter)
        
        DEFAULT_CONTROLLER.on = True

        say(SpeechLines.ECOTRON_READY)
        logger.info("*** Ecotron startup complete ***")

class EcotronControls:
    def __init__(self, mcp23017a_1, mcp23017a_2, mcp23017a_3, mcp3008a):
        self.elevator_controls = ElevatorControls(mcp23017a_1)
        self.conveyor_controls = ConveyorControls(mcp23017a_1, mcp3008a)
        self.toggle_board = ToggleBoard([Toggle(mcp23017a_2.get_pin(idx)) for idx in range(10)])

        self.color_dials = ColorDials(
            Encoder(mcp23017a_3.get_pin(1), mcp23017a_3.get_pin(0)),
            Encoder(mcp23017a_3.get_pin(3), mcp23017a_3.get_pin(2)),
            Encoder(mcp23017a_3.get_pin(5), mcp23017a_3.get_pin(4)),
            Encoder(mcp23017a_3.get_pin(7), mcp23017a_3.get_pin(6)),
            Encoder(mcp23017a_3.get_pin(8), mcp23017a_3.get_pin(9))            
        )

class EcotronBase:
    def __init__(self, hub, servo_kit_1, servo_kit_2, neopixels, controls, director, properties, color_controller):

            np_tl_jungle = NeopixelSegment(neopixels, 0, 8) 

            np_fl_1_1 = Neopixels(neopixels, 8, 1)
            np_hyperscanner_outer = NeopixelSegment(neopixels, 9, 1)
            np_hyperscanner_inner = NeopixelSegment(neopixels, 10, 1)
            np_fl_1_2 = Neopixels(neopixels, 11, 15)
            np_conveyor_receiver = NeopixelSegment(neopixels, 26, 1)
            np_fl_1_3 = Neopixels(neopixels, 27, 2)

            np_fl_2_1 = Neopixels(neopixels, 29, 10, reversed=True)
            np_door = Neopixels(neopixels, 39, 3)

            np_tl_1 = NeopixelSegment(neopixels, 42, 22)

            np_elevator = NeopixelSegment(neopixels, 64, 12)

# neopixel 16 = machoine

            properties.master_volume.on_value_change = lambda x : set_master_volume(x)

            self.top_lights_jungle = Lights(np_tl_jungle, properties.top_lights_jungle_color, color_controller=color_controller)
            self.top_lights_jungle.bind_to_property(properties.top_lights_jungle_on)

            self.door_lights = Lights(NeopixelMultiSegment(np_door), properties.door_lights_color, color_controller=color_controller)
            self.door_lights.bind_to_property(properties.door_lights_on)
            
            self.floor_lights = floor_lights(
                NeopixelMultiSegment(np_fl_1_1, FakeNeopixels(2), np_fl_1_2, FakeNeopixels(2), np_fl_1_3, np_fl_2_1),
                properties.floor_lights_color, color_controller=color_controller
                )
            self.floor_lights.bind_to_property(properties.light_strip_on)

            self.top_lights_floor_1 = Lights(np_tl_1, properties.top_lights_floor_1_color, color_controller=color_controller)
            self.top_lights_floor_1.bind_to_property(properties.top_lights_floor_1_on)

            self.elevator = Elevator(director, controls.elevator_controls, hub.device("A"), np_elevator, properties)

            self.conveyor = Conveyor(hub.device("D"), controls.conveyor_controls, director)
            self.bebop = Bebop(director, Servo(servo_kit_1.servo[13]), PWMLED(servo_kit_1._pca.channels[14]))            
            self.hyperscanner = Hyperscanner(np_hyperscanner_inner, np_hyperscanner_outer)
            self.conveyor_receiver = ConveyorReceiver(np_conveyor_receiver)
            
            self.repair_table = RepairTable(director, PWMLED(servo_kit_2._pca.channels[7]), PWMLED(servo_kit_2._pca.channels[8]), Servo(servo_kit_1.servo[15]))
            self.repair_table.bind_to_property(properties.repair_table_on)

            self.fans = Fans(hub.device("C"))
            self.fans.bind_to_property(properties.fans_on)

            self.jungle = Jungle([
                PWMLED(servo_kit_2._pca.channels[2]),
                PWMLED(servo_kit_2._pca.channels[3]),
                PWMLED(servo_kit_2._pca.channels[4]),
                PWMLED(servo_kit_2._pca.channels[5]),
                PWMLED(servo_kit_2._pca.channels[6]),                
            ])
            self.jungle.bind_to_property(properties.jungle_on)


class MasterController:
    def __init__(self, base):
        self._base = base
        self.metatron_on = True

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
    conveyor_controls.master_switch.on_press = scripter.production_line.production_line_on
    conveyor_controls.master_switch.on_release = scripter.production_line.production_line_off


def bind_controls_to_properties(controls, properties):
    
    controls.toggle_board.toggles[0].bind_property(properties.top_lights_jungle_on)
    controls.toggle_board.toggles[1].bind_property(properties.top_lights_floor_1_on)
    controls.toggle_board.toggles[2].bind_property(properties.light_strip_on)
    controls.toggle_board.toggles[3].bind_property(properties.elevator_lights_on)
    controls.toggle_board.toggles[4].bind_property(properties.door_lights_on)

    controls.toggle_board.toggles[5].bind_property(properties.master_volume)
    controls.toggle_board.toggles[6].bind_property(properties.fans_on)
    controls.toggle_board.toggles[7].bind_property(properties.repair_table_on)
    controls.toggle_board.toggles[8].bind_property(properties.jungle_on)



def bind_controls_to_actions(controls, base, master_controller, scripter):
    bind_elevator(base.elevator, controls.elevator_controls)
    bind_conveyor_controls(controls.conveyor_controls, master_controller, base, scripter)


