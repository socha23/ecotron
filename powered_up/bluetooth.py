from bluepy.btle import Scanner, DefaultDelegate, Peripheral
from queue import Queue
from threading import Thread
from time import sleep
from powered_up.messages import decode_upstream_message, HubAction, HubActionIds

import logging


logger = logging.getLogger(__name__)

# Tries to connect to a device with a given MAC address. 
# Blocks until the device is found and connected to. Returns Peripheral representing the device or None if nothing was found after timeout.
def connect_ble(mac_address, timeout=600):

    class ScanDelegate(DefaultDelegate):
        def __init__(self):
            DefaultDelegate.__init__(self)
            self.scan_result = None

        def handleDiscovery(self, dev, is_new_dev, is_new_data):
            if is_new_dev and dev.addr == mac_address:                
                self.scan_result = dev

    delegate = ScanDelegate()
    scanner = Scanner().withDelegate(delegate)
    scanner.clear()
    scanner.start()
    logger.info(f'Looking for device {mac_address}...')
    for _ in range(timeout):
        scanner.process(1)
        if delegate.scan_result != None:
            break
    scanner.stop()
    if delegate.scan_result == None:
        logger.info(f'Timed out looking for device {mac_address}')
        return None
    else:
        logger.info(f'Found device {mac_address}')
        peripheral = Peripheral(delegate.scan_result.addr, delegate.scan_result.addrType)
        # enable notifications
        peripheral.writeCharacteristic(0x000f, b'\x01\x00')
        return BleConnection(peripheral)


class BleConnection:    
    def __init__(self, peripheral):
        self._queue = Queue()
        self.on_upstream_message = lambda _: None
        SenderReceiverThread(peripheral, self._queue, self._on_upstream_message).start()

    def send(self, message):
        self._queue.put(message)

    def _on_upstream_message(self, message):
        self.on_upstream_message(message)


TIME_SLICE = 0.05 # 20 FPS
KEEPALIVE = 0.5 

class SenderReceiverThread(Thread, DefaultDelegate):

    def __init__(self, peripheral, queue, upstream_message_handler):
        Thread.__init__(self, daemon=True)
        DefaultDelegate.__init__(self)
        self._queue = queue
        self._upstream_message_handler = upstream_message_handler
        self._peripheral = peripheral.withDelegate(self)

    def run(self):
        while True:
            for _ in range(int(KEEPALIVE / TIME_SLICE)):
                while not self._queue.empty():
                    message = self._queue.get()
                    logger.debug(f"Send: {message}")
                    self._peripheral.writeCharacteristic(0x0E, message.bytes())
                notification_received = True
                while notification_received:
                    notification_received = self._peripheral.waitForNotifications(TIME_SLICE)            
                sleep(TIME_SLICE)
            # There is some bug with bluepy with some notifications delivered only when next downstream message is sent.
            # To work around it, every KEEPALIVE we send 'reset busy indicator' as a no-op so that messages are properly delivered
            self._peripheral.writeCharacteristic(0x0E, HubAction(HubActionIds.RESET_BUSY_INDICATOR).bytes())

    def handleNotification(self, handle, data):
        message = decode_upstream_message(data)
        logger.debug(f"Recv: {message}")
        self._upstream_message_handler(message)


