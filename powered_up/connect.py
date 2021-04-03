from threading import Thread
from time import sleep
from powered_up.hub import Hub
from powered_up.bluetooth import connect_ble

def connect_technic_hub(mac_address, led_to_blink_while_connecting=None, led_to_turn_on_when_connected=None):
    hub = Hub()
    _ConnectionThread(mac_address, hub, led_to_blink_while_connecting, led_to_turn_on_when_connected).start()
    return hub


class _ConnectionThread(Thread):
    def __init__(self, mac_address, hub, led_to_blink_while_connecting, led_to_turn_on_when_connected):
        Thread.__init__(self, daemon=True)
        self._mac_address = mac_address
        self._hub = hub
        self._led_to_blink_while_connecting = led_to_blink_while_connecting
        self._led_to_turn_on_when_connected = led_to_turn_on_when_connected
    
    def run(self):
        self._led_to_blink_while_connecting.blink()
        connection = connect_ble(self._mac_address)        
        self._led_to_blink_while_connecting.off()
        if connection != None:
            if self._led_to_turn_on_when_connected != None:
                self._led_to_turn_on_when_connected.on()
            self._hub.connect(connection)
