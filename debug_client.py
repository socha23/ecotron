from powered_up.debug import connect_debug_technic_hub
from powered_up.mac import ECOTRON_TECHNIC_HUB_MAC

from ecotron import Ecotron
import logging
from time import sleep

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    #hub = connect_technic_hub(TECHNIC_HUB_MAC, led_red, led_green)
    hub = connect_debug_technic_hub()

    ecotron = Ecotron(hub)

    while True:
        sleep(1)