import logging
from powered_up.messages import PortInputFormatSetupSingle, AttachedIO, is_port_internal, IOTypeIds, UpstreamMessage
from powered_up.devices import RGBLED, instantiate_device

logger = logging.getLogger(__name__)

class Hub:
    def __init__(self):
        self._connection = None
        self._devices_on_ports = dict()
        self._on_connect_device = dict()
        self._internal_led = RGBLED()

    def is_connected(self):
        return self._connection != None

    def connect(self, connection):
        self._connection = connection
        connection.on_upstream_message = self.handle_upstream_message

    def send(self, message):
        if not self.is_connected():
            logger.debug("Trying to send a message to a disconnected hub")
        else:
            self._connection.send(message)

    def device(self, port_letter):
        return self._devices_on_ports.get(ord(port_letter) - ord("A"))

    def set_on_connect(self, port_letter, on_connect):
        self._on_connect_device[ord(port_letter) - ord("A")] = on_connect

    def handle_upstream_message(self, message):
        if isinstance(message, AttachedIO):
            port = Port(self, message.port_id())        
            if message.device_id() == IOTypeIds.RGB_LIGHT:
                self._internal_led.set_port(port)
                self._internal_led.value = (255, 128, 0)
            elif not is_port_internal(message.port_id()):
                device = instantiate_device(message.device_id(), port)
                logger.debug(f"registering device {device} on port {port}")
                self._devices_on_ports[message.port_id()] = device
                handler = self._on_connect_device.get(message.port_id())
                if handler != None:
                    handler(device)
        elif isinstance(message, UpstreamMessage) and hasattr(message, "port_id"):
            device = self._devices_on_ports.get(message.port_id())
            if device != None and hasattr(device, "on_upstream_message"):
                device.on_upstream_message(message)

    def internal_led(self):
        return self._internal_led

    def wait_for_devices(self, *args):
        while True:
            missing_devices = []
            for needed_device in args:
                found_device = self.device(needed_device)
                if found_device == None or (hasattr(found_device, "is_initialized") and not found_device.is_initialized()):
                    missing_devices.append(needed_device)
                if not self._internal_led.is_connected():
                    missing_devices.append("Internal LED")
            if not missing_devices:
                self._internal_led.value = (0, 255, 0)
                break
            else:
                logger.debug(f"Waiting for devices: {missing_devices}")


class Port:
    def __init__(self, hub, port_id):
        self._hub = hub
        self._port_id = port_id
        self._mode = None
        self._delta_interval = None
        self._notification_enabled = None

    def set_mode(self, mode, delta_interval=1, notification_enabled=False):
        if self._mode == mode and self._delta_interval == delta_interval and self._notification_enabled == notification_enabled:
            return # port is set right, skip
        self._mode = mode
        self._delta_interval = delta_interval
        self._notification_enabled = notification_enabled
        self._hub.send(PortInputFormatSetupSingle(self._port_id, mode, delta_interval, notification_enabled))

    def send(self, message):
        return self._hub.send(message)

    def port_id(self):
        return self._port_id

    def __repr__(self):
        return f"Port {self._port_id}"


