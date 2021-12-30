from ecotron.reactor import Reactor, ReactorDoor, ReactorWarningLights
from ecotron.color_controller import DEFAULT_COLOR_CONTROLLER
from ecotron.laboratory import Laboratory
from ecotron.aquarium import Aquarium
from ecotron.stairsdude import Stairsdude
from ecotron.spiderbro import Spiderbro
from ecotron.widget import MultiWidget
import board
from busio import I2C, SPI
from digitalio import DigitalInOut
from components.buffering_mcp23017 import BufferingMcp23017
from adafruit_mcp3xxx.mcp3008 import MCP3008
from adafruit_mcp3xxx.analog_in import AnalogIn
from adafruit_servokit import ServoKit
import logging

from adafruit_mcp3xxx.mcp3008 import P1

from director import DEFAULT_DIRECTOR
from ecotron.conveyor import Conveyor, ConveyorControls
from ecotron.conveyor_receiver import ConveyorReceiver
from ecotron.hyperscaner import Hyperscanner

from ecotron.elevator import Elevator, ElevatorControls
from ecotron.repair_table import RepairTable
from ecotron.bebop import Bebop
from ecotron.fans import Fans
from ecotron.airlock import Airlock
from ecotron.properties import DEFAULT_ECOTRON_PROPERTIES
from components.toggle import Toggle, ToggleBoard
from components.encoder import Encoder
from components.servo import Servo
from components.led import PWMLED
from components.neopixels import NeopixelStrip, NeopixelSegment, NeopixelMultiSegment, FakeNeopixels, Neopixels
from components.color_dials import ColorDials
from tick_aware import DEFAULT_CONTROLLER
from speech import say, SpeechLines
from sound import set_master_volume
from ecotron.lights import Lights
from ecotron.jungle import Jungle

logger = logging.getLogger(__name__)

mcp23017a_1 = BufferingMcp23017(I2C(board.SCL, board.SDA), address=0x20)
mcp23017a_2 = BufferingMcp23017(I2C(board.SCL, board.SDA), address=0x21)
mcp23017a_3 = BufferingMcp23017(I2C(board.SCL, board.SDA), address=0x22)
mcp23017a_4 = BufferingMcp23017(I2C(board.SCL, board.SDA), address=0x23)
spi = SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = DigitalInOut(board.D5)
mcp3008a = MCP3008(spi, cs)
servo_kit_1 = ServoKit(channels=16, reference_clock_speed=25000000)
servo_kit_2 = ServoKit(channels=16, address=0x41)
servo_kit_3 = ServoKit(channels=16, address=0x42)
neopixels = NeopixelStrip(board.D21, 137)

class Ecotron:
    def __init__(self, hub):
        logger.info("*** Ecotron startup ***")
        hub.wait_for_devices("A", "B", "C", "D")

        controls = EcotronControls()
        properties = DEFAULT_ECOTRON_PROPERTIES

        controls.color_dials.bind(DEFAULT_COLOR_CONTROLLER)

        bind_controls_to_properties(controls, properties)

        director = DEFAULT_DIRECTOR
        base = EcotronBase(hub, controls, director, properties, DEFAULT_COLOR_CONTROLLER)

        bind_controls_to_actions(controls, base)

        DEFAULT_CONTROLLER.on = True

        say(SpeechLines.ECOTRON_READY)
        logger.info("*** Ecotron startup complete ***")

class EcotronControls:
    def __init__(self):
        self.elevator_controls = ElevatorControls(mcp23017a_1)
        self.conveyor_controls = ConveyorControls(mcp23017a_1, mcp3008a)

        self.control_toggle_board = ToggleBoard([Toggle(mcp23017a_4.get_pin(idx)) for idx in range(10)])

        self.light_toggle_board = ToggleBoard([Toggle(mcp23017a_2.get_pin(idx)) for idx in range(10)])
        self.color_dials = ColorDials(
            Encoder(mcp23017a_3.get_pin(1), mcp23017a_3.get_pin(0)),
            Encoder(mcp23017a_3.get_pin(3), mcp23017a_3.get_pin(2)),
            Encoder(mcp23017a_3.get_pin(5), mcp23017a_3.get_pin(4)),
            Encoder(mcp23017a_3.get_pin(7), mcp23017a_3.get_pin(6)),
            Encoder(mcp23017a_3.get_pin(8), mcp23017a_3.get_pin(9))
        )

class EcotronBase:
    def __init__(self, hub, controls, director, properties, color_controller):

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


            np_aquarium_start = 64
            np_aqua_0 = NeopixelSegment(neopixels, np_aquarium_start, 5)
            np_aqua_1 = NeopixelMultiSegment(Neopixels(neopixels, np_aquarium_start + 5, 5, reversed=True))
            np_aqua_2 = NeopixelSegment(neopixels, np_aquarium_start + 10, 5)
            np_aqua_3 = NeopixelMultiSegment(Neopixels(neopixels, np_aquarium_start + 15, 5, reversed=True))

            # px 84
            np_reactor_fans = NeopixelSegment(neopixels, 84, 4)

            # px 88

            np_fl_1_4 = Neopixels(neopixels, 88, 8, reversed=True)

            # px 96

            np_reactor_main = NeopixelSegment(neopixels, 96, 10)

            # px 106
            np_laboratory_main_lights = NeopixelSegment(neopixels, 106, 8)
            np_top = NeopixelSegment(neopixels, 114, 2)
            np_laboratory_stalker = NeopixelSegment(neopixels, 116, 2)
            # 1 dead
            np_laboratory_between_tanks = NeopixelSegment(neopixels, 119, 1)
            # 1 dead
            np_laboratory_tentacle = NeopixelSegment(neopixels, 121, 2)

            # px 124

            np_elevator = NeopixelSegment(neopixels, 125, 12)


            properties.master_volume.on_value_change = lambda x : set_master_volume(x)

            self.aquarium = Aquarium([np_aqua_0, np_aqua_1, np_aqua_2, np_aqua_3])
            self.aquarium.bind_to_property(properties.aquarium_lights_on)

            self.top_lights_jungle = Lights(np_tl_jungle, properties.top_lights_jungle)
            self.door_lights = Lights(NeopixelMultiSegment(np_door), properties.door_lights)

            self.light_strip = Lights(
                NeopixelMultiSegment(np_fl_1_1, FakeNeopixels(2), np_fl_1_2, FakeNeopixels(2), np_fl_1_3,
                np_fl_1_4,
                np_fl_2_1,
                ),
                properties.light_strip)

            self.top_lights_floor_1 = Lights(np_tl_1, properties.top_lights_floor_1)

            self.elevator = Elevator(director, controls.elevator_controls, hub.device("A"), np_elevator, properties)

            self.conveyor = Conveyor(hub.device("D"), analog_read(mcp3008a, P1), director)
            self.hyperscanner = Hyperscanner(np_hyperscanner_inner, np_hyperscanner_outer, director)
            self.conveyor_receiver = ConveyorReceiver(np_conveyor_receiver)
            self.bebop = Bebop(
                Servo(servo_kit_1.servo[13], min_pulse_witdh_range=700, max_pulse_witdh_range=2650),
                PWMLED(servo_kit_1._pca.channels[14])
            )
            self.conveyor.on_move_complete_listeners.append(self.hyperscanner.run_scan_cycle)
            self.conveyor.add_phase_listener(0.3, self.conveyor_receiver.flash_ok)
            self.bebop.observe_conveyor(self.conveyor)
            MultiWidget(
              self.conveyor,
              self.hyperscanner,
              self.conveyor_receiver,
              self.bebop
            ).bind_to_property(properties.conveyor_on)

            self.repair_table = RepairTable(PWMLED(servo_kit_2._pca.channels[7]), PWMLED(servo_kit_2._pca.channels[8]), Servo(servo_kit_1.servo[15]))
            self.repair_table.bind_to_property(properties.repair_table_on)

            self.fans = Fans(hub.device("C"))
            self.stairsdude = Stairsdude(Servo(servo_kit_1.servo[12], min_pulse_witdh_range=700, max_pulse_witdh_range=2650))
            MultiWidget(self.fans, self.stairsdude).bind_to_property(properties.fans_on)

            self.airlock = Airlock(
                    inner_red=PWMLED(servo_kit_1._pca.channels[10]),
                    inner_green=PWMLED(servo_kit_1._pca.channels[9]),
                    inner_door_servo=Servo(servo_kit_1.servo[11]),
                    inner_angle_closed=180, inner_angle_open=60,
                    outer_red=PWMLED(servo_kit_1._pca.channels[7]),
                    outer_green=PWMLED(servo_kit_1._pca.channels[6]),
                    outer_door_servo=Servo(servo_kit_1.servo[8]),
                    outer_angle_closed=0, outer_angle_open=120,
            )

            self.jungle = Jungle([
                PWMLED(servo_kit_2._pca.channels[2]),
                PWMLED(servo_kit_2._pca.channels[3]),
                PWMLED(servo_kit_2._pca.channels[4]),
                PWMLED(servo_kit_2._pca.channels[5]),
                PWMLED(servo_kit_2._pca.channels[6]),
            ])
            self.spiderbro = Spiderbro(
                Servo(servo_kit_2.servo[0], min_pulse_witdh_range=700, max_pulse_witdh_range=2650),
                PWMLED(servo_kit_2._pca.channels[1])
            )
            MultiWidget(self.spiderbro, self.jungle).bind_to_property(properties.jungle_on)

            self.reactor_door = ReactorDoor(
                Servo(servo_kit_3.servo[11], min_pulse_witdh_range=700, max_pulse_witdh_range=2650)
            )
            self.reactor_door.bind_to_property(properties.reactor_door_open)
            self.reactor_lights = ReactorWarningLights(
                PWMLED(servo_kit_3._pca.channels[10]),
                PWMLED(servo_kit_3._pca.channels[9]),
            )
            self.reactor_lights.bind_to_property(properties.reactor_lights_on)
            self.reactor_fan_lights = Lights(np_reactor_fans, properties.reactor_fan_lights)
            self.reactor = Reactor(np_reactor_main)

            self.laboratory = Laboratory(
                stretch_servo=Servo(servo_kit_3.servo[15], angle=140, min_pulse_witdh_range=600, max_pulse_witdh_range=2900),
                rotate_servo=Servo(servo_kit_3.servo[14], angle=110, min_pulse_witdh_range=600, max_pulse_witdh_range=2900),
                uprighter_servo=Servo(servo_kit_3.servo[13], angle=20, min_pulse_witdh_range=700, max_pulse_witdh_range=2900),
                chair_servo=Servo(servo_kit_3.servo[12], angle=180, min_pulse_witdh_range=700, max_pulse_witdh_range=2900),
                stalk_servo=Servo(servo_kit_3.servo[7], angle=80, min_pulse_witdh_range=700, max_pulse_witdh_range=2900),
                siren_led=PWMLED(servo_kit_3._pca.channels[8]),
                top_light_pixels=np_laboratory_main_lights,
                stalker_light_pixels=np_laboratory_stalker,
                tentacle_light_pixels=np_laboratory_tentacle,
            )
            self.laboratory.bind_to_property(properties.laboratory_on)


def bind_controls_to_properties(controls, properties):

    controls.conveyor_controls.toggle.bind_property(properties.master_volume, properties.control_panel_ligths_on)

    control_toggles = controls.control_toggle_board.toggles

    control_toggles[0].bind_property(properties.jungle_on)
    control_toggles[1].bind_property(properties.repair_table_on)
    control_toggles[4].bind_property(properties.laboratory_on)
    control_toggles[5].bind_property(properties.conveyor_on)
    control_toggles[7].bind_property(properties.fans_on)
    control_toggles[8].bind_property(properties.laboratory_on)
    control_toggles[9].bind_property(properties.reactor_door_open)

    light_toggles = controls.light_toggle_board.toggles

    light_toggles[0].bind_property(properties.top_lights_jungle.on)
    light_toggles[1].bind_property(
        # order is important, last one will take color controller
        properties.door_lights.on,
        properties.top_lights_floor_1.on,
        )
    light_toggles[2].bind_property(properties.laboratory_stalker_lights.on)
    light_toggles[3].bind_property(properties.laboratory_tentacle_lights.on)
    light_toggles[4].bind_property(properties.laboratory_top_lights.on)

    light_toggles[5].bind_property(properties.light_strip.on)
    light_toggles[7].bind_property(properties.aquarium_lights_on)
    light_toggles[8].bind_property(properties.reactor_fan_lights.on)
    light_toggles[9].bind_property(properties.reactor_lights_on)


def bind_controls_to_actions(controls, base):

    for floor_idx in range(len(Elevator.FLOOR_HEIGHTS)):
            controls.elevator_controls.floor_buttons[floor_idx].on_press = lambda floor_idx=floor_idx: base.elevator.go_to_floor(floor_idx)

    controls.elevator_controls.button_red.on_press = DEFAULT_ECOTRON_PROPERTIES.print_properties
   # controls.elevator_controls.button_green.on_press = base.laboratory.blitz_tentacle

    controls.conveyor_controls.button_blue.on_press = base.airlock.run_cycle_from_outside

    controls.conveyor_controls.button_yellow.on_press = base.laboratory.button_press
    controls.conveyor_controls.button_yellow.on_release = base.laboratory.button_release

    controls.conveyor_controls.button_green.on_press = base.stairsdude.random_rotation
    controls.conveyor_controls.button_red.on_press = base.reactor.boom


def analog_read(mcp, pin):
  analog_in = AnalogIn(mcp, pin)
  return lambda: analog_in.value / 65536
