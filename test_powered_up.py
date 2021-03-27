from powered_up.connect import connect_technic_hub
from powered_up.debug import connect_debug_technic_hub
from powered_up.devices import InterruptableMotor
from ecotron.conveyor import Conveyor
from ecotron.elevator import Elevator

from time import sleep
from threading import Thread
import logging

logging.basicConfig(level=logging.INFO)

MOVE_HUB_MAC = "00:16:53:a8:ec:58"
TECHNIC_HUB_MAC = "90:84:2b:5c:2b:9e"

#hub = connect_technic_hub(TECHNIC_HUB_MAC, led_red, led_green)
hub = connect_debug_technic_hub()
hub.internal_led().value = (255, 128, 0)

print("Ready!")
input()
hub.internal_led().value = (0, 255, 0)

conveyor = Conveyor(hub.device("D"), 5)
conveyor.speed = 0.25
conveyor.wait_time = 1
#conveyor.start(125)

elevator = Elevator(InterruptableMotor(hub.device("A")))

elevator.reset()
print("enter pos, or empty to quit")
command = input()
while command != "":
    move = float(command)
    print(f"moving {move}")
    elevator.move(move)
    command = input()

hub.internal_led().value = (255, 0, 0)
elevator.stop()
conveyor.stop()


