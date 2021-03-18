from threading import Thread
from time import sleep
from powered_up.hub import TechnicHub
from powered_up.bluetooth import connect_ble

def connect_technic_hub(mac_address, led_to_blink_while_connecting=None, led_to_turn_on_when_connected=None):
    hub = TechnicHub()
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
        blink_thread = _BlinkThread(self._led_to_blink_while_connecting)
        blink_thread.start()
        connection = connect_ble(self._mac_address)        
        blink_thread.stop()
        blink_thread.join()
        if connection != None:
            if self._led_to_turn_on_when_connected != None:
                self._led_to_turn_on_when_connected.on()
            self._hub.connect(connection)
        
        
class StoppableThread(Thread):
    def __init__(self):
        Thread.__init__(self, daemon=True)
        self._stopped = False
    
    def is_stopped(self):
        return self._stopped

    def stop(self):
        self._stopped = True


class _BlinkThread(StoppableThread):
    def __init__(self, led):
        StoppableThread.__init__(self)
        self._led = led

    def _led_on(self):
        if self._led != None:
            self._led.on()

    def _led_off(self):
        if self._led != None:
            self._led.off()

    def run(self):
        while not self.is_stopped():
            self._led_on()
            sleep(1)
            if not self.is_stopped():
                self._led.off()
                sleep(1)
        self._led_off()
