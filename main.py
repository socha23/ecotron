import board
from digitalio import DigitalInOut
from time import sleep

from components.led import LED
from ecotron import Ecotron
from powered_up.connect import connect_technic_hub
from powered_up.mac import ECOTRON_TECHNIC_HUB_MAC
from tick_aware import DEFAULT_CONTROLLER

def led_on_pin(pin_no):
    return LED(DigitalInOut(pin_no))

if __name__ == '__main__':
    sleep(5)
    DEFAULT_CONTROLLER.on = True
    hub = connect_technic_hub(ECOTRON_TECHNIC_HUB_MAC, led_on_pin(board.D27), led_on_pin(board.D22))
    ecotron = Ecotron(hub)

    while True:
        sleep(1)
