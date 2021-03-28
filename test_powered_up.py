from powered_up.connect import connect_technic_hub
from powered_up.debug import connect_debug_technic_hub
from ecotron import Ecotron
from ecotron.elevator import Elevator, ElevatorControls
from tick_aware import DEFAULT_CONTROLLER

from time import sleep
import logging

logging.basicConfig(level=logging.INFO)

MOVE_HUB_MAC = "00:16:53:a8:ec:58"
TECHNIC_HUB_MAC = "90:84:2b:5c:2b:9e"

#hub = connect_technic_hub(TECHNIC_HUB_MAC, led_red, led_green)
hub = connect_debug_technic_hub()
hub.internal_led().value = (255, 128, 0)

print("Please press enter to connect Ecotron")
input()
hub.internal_led().value = (0, 255, 0)
ecotron = Ecotron(hub)


DEFAULT_CONTROLLER.on = True
while True:
    sleep(1)