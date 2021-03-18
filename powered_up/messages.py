from struct import pack, unpack
from powered_up.utils import as_byte, as_int

class MessageTypeIds:
    HUB_PROPERTIES = 0x01
    HUB_ACTION = 0x02
    HUB_ATTACHED_IO = 0x04
    HUB_ERROR = 0x05
    PORT_INPUT_FORMAT_SETUP_SINGLE = 0x41
    PORT_INPUT_FORMAT_SINGLE = 0x47
    PORT_OUTPUT = 0x81
    PORT_OUTPUT_FEEDBACK = 0x82
    PORT_VALUE_SINGLE = 0x45
    PORT_INFORMATION_REQUEST = 0x21

class DownstreamMessage:
    def __init__(self, type):
        self._type = type

    def length(self):
        # 3 bytes for common header
        return 3 + len(self.get_payload())

    def bytes(self):
        return as_byte(self.length()) + as_byte(0x00) + as_byte(self._type) + self.get_payload()

    def get_payload(self):
        raise "Not implemented"

    def __repr__(self):
        return f'Message({self.bytes().hex()})'

    def to_int8(self, val):
        return pack("<b", val)

    def to_uint8(self, val):
        return pack("<B", val)

    def to_int16(self, val):
        return pack("<h", val)

    def to_uint16(self, val):
        return pack("<H", val)

    def to_int32(self, val):
        return pack("<i", val)

    def to_uint32(self, val):
        return pack("<I", val)

class UpstreamMessage:
    def __init__(self, bytes):
        self._bytes = bytes

    def length(self):
        return len(self._bytes)

    def payload(self):
        return self._bytes[3:]

    def bytes(self):
        return self._bytes

    def __repr__(self):
        return f'Message({self.bytes().hex()})'

    def payload_uint8(self, idx):
        return unpack("<B", self.payload()[idx : idx + 1])[0]

    def payload_uint16(self, idx):
        return unpack("<H", self.payload()[idx : idx + 2])[0]

    def payload_uint32(self, idx):
        return unpack("<I", self.payload()[idx : idx + 4])[0]

    def payload_int8(self, idx):
        return unpack("<b", self.payload()[idx : idx + 1])[0]

    def payload_int16(self, idx):
        return unpack("<h", self.payload()[idx : idx + 2])[0]

    def payload_int32(self, idx):
        return unpack("<i", self.payload()[idx : idx + 4])[0]

##################################################################################################
# DEBUG
##################################################################################################

DEBUG_REPLAY_ATTACHED_IO_BYTES = b"replayatachedio"

class DebugReplayAttachedIO:
    def bytes(self):
        return DEBUG_REPLAY_ATTACHED_IO_BYTES

    def __repr__(self):
        return f'Debug server, please replay attached IO devices'        

class DebugDownstreamMessage:
    def __init__(self, msg_bytes):
        self._bytes = msg_bytes

    def bytes(self):
        return self._bytes

    def __repr__(self):
        return f'Debug server downstream message {self._bytes.hex()}'

##################################################################################################
# PROPERTIES
##################################################################################################

class HubPropertyIds:
    ADVERTISING_NAME = 0x01
    BUTTON = 0x02
    FW_VERSION = 0x03
    HW_VERSION = 0x04
    RSSI = 0x05
    BATTERY_VOLTAGE_PERC = 0x06
    BATTERY_TYPE = 0x07
    MANUFACTURER = 0x08
    RADIO_FW_VERSION = 0x09
    WIRELESS_PROTOCOL_VERSION = 0x0A
    SYSTEM_TYPE_ID = 0x0B
    HW_NETW_ID = 0x0C
    PRIMARY_MAC_ADDRESS = 0x0D
    SECONDARY_MAC_ADDRESS = 0x0E
    HARDWARE_NETWORK_FAMILY = 0x0F

class HubPropertyOperations:
    SET = 0x01
    ENABLE_UPDATES = 0x02
    DSABLE_UPDATES = 0x03
    RESET = 0x04
    REQUEST_UPDATE = 0x05
    UPDATE = 0x06
    

class RequestPropertyUpdate(DownstreamMessage):    
    def __init__(self, property_id):
        DownstreamMessage.__init__(self, MessageTypeIds.HUB_PROPERTIES)
        self._property_id = property_id

    def get_payload(self):
        return as_byte(self._property_id) + as_byte(HubPropertyOperations.REQUEST_UPDATE)

    def __repr__(self):
        return f'Property update request for {value_name(HubPropertyIds, self._property_id)}'

class PropertyUpdate(UpstreamMessage):
    def __init(self, bytes):
        UpstreamMessage.__init__(self, bytes)

    def property_id(self):
        return as_int(self.payload()[0:1])

    def __repr__(self):
        return f'Property update for {value_name(HubPropertyIds, self.property_id())}: {self.payload()[2:].hex()}'

##################################################################################################
# ACTIONS
##################################################################################################

class HubActionIds:
    SWITCH_OFF = 0x01
    DISCONNECT = 0x02
    VCC_PORT_ON = 0x03
    VCC_PORT_OFF = 0x04
    ACTIVATE_BUSY_INDICATOR = 0x05
    RESET_BUSY_INDICATOR = 0x06

class HubAction(DownstreamMessage):    
    def __init__(self, action_id):
        DownstreamMessage.__init__(self, MessageTypeIds.HUB_ACTION)
        self._action_id = action_id

    def get_payload(self):
        return as_byte(self._action_id)

    def __repr__(self):
        return f'Action called: {value_name(HubActionIds, self._action_id)}'

##################################################################################################
# Errors
##################################################################################################

class ErrorCodes:
    ACK = 0x01
    MACK = 0x02
    BUFFER_OVERFLOW = 0x03
    TIMEOUT = 0x04
    COMMAND_NOT_RECOGNIZED = 0x05
    INVALID_USE = 0x06
    OVERCURRENT = 0x07
    INTERNAL_ERROR = 0x08

class HubError(UpstreamMessage):    

    def __init__(self, bytes):
        UpstreamMessage.__init__(self,  bytes)
        self._command_id = self.payload_uint8(0)
        self._error_code = self.payload_uint8(1)

    def __repr__(self):
        return f'Error for command {value_name(MessageTypeIds, self._command_id)}: {value_name(ErrorCodes, self._error_code)}'
##################################################################################################
# IO
##################################################################################################

class IOTypeIds:
    MOTOR = 0x0001
    SYSTEM_TRAIN_MOTOR = 0x0002
    BUTTON = 0x0005
    LED_LIGHT = 0x0008
    VOLTAGE = 0x0014
    CURRENT = 0x0015
    PIEZO = 0x0016
    RGB_LIGHT = 0x0017
    EXTERNAL_TILT = 0x0022
    MOTION_SENSOR = 0x0023
    VISION_SENSOR = 0x0025
    EXTERNAL_MOTOR_TACHO = 0x0026
    INTERNAL_MOTOR_TACHO = 0x0027
    INTERNAL_TILT = 0x0028

class AttachedIO(UpstreamMessage):    

    def __init__(self, bytes):
        UpstreamMessage.__init__(self,  bytes)

    def port_id(self):
        return self.payload_uint8(0)

    def port_desc(self):
        return port_desc(self.port_id())

    def is_attached(self):
        e = self.payload_uint8(1)
        return e == 1

    def device_id(self):
        return self.payload_uint16(2)        

    def device_desc(self):
        return value_name(IOTypeIds, self.device_id())

    def __repr__(self):
        if self.is_attached():
            return f'Attached {self.device_desc()} on {self.port_desc()}'
        else:
            return f'Detached device from {self.port_desc()}'

##################################################################################################
# Port setup
##################################################################################################

class PortInputFormatSetupSingle(DownstreamMessage):
    def __init__(self, port, mode, delta_interval=1, notification_enabled = False):
        DownstreamMessage.__init__(self, MessageTypeIds.PORT_INPUT_FORMAT_SETUP_SINGLE)
        self._port = port
        self._mode = mode
        self._delta_interval = delta_interval
        self._notification_enabled = notification_enabled

    def get_payload(self):
        return self.to_uint8(self._port) + self.to_uint8(self._mode) + self.to_uint32(self._delta_interval) + self.to_uint8(1 if self._notification_enabled else 0)


    def __repr__(self):
         return f'Set port {port_desc(self._port)} to mode {self._mode}, delta interval {self._delta_interval}, notification {"enabled" if self._notification_enabled else "disabled"}'
    
class PortInputFormatSingle(UpstreamMessage):
    def __init__(self, bytes):
        UpstreamMessage.__init__(self, bytes)
        self._port = self.payload_uint8(0)
        self._mode = self.payload_uint8(1)
        self._delta_interval = self.payload_uint32(2)
        self._notification_enabled = self.payload_uint8(6) == 1

    def __repr__(self):
         return f'Port {port_desc(self._port)} set to mode {self._mode}, delta interval {self._delta_interval}, notification {"enabled" if self._notification_enabled else "disabled"}'

##################################################################################################
# Port input
##################################################################################################

class PortValueRequest(DownstreamMessage):
    def __init__(self, port):
        DownstreamMessage.__init__(self, MessageTypeIds.PORT_INFORMATION_REQUEST)
        self._port = port

    def get_payload(self):
        return self.to_uint8(self._port) + self.to_uint8(0x00)


    def __repr__(self):
         return f'Request value from port {port_desc(self._port)}'
 

class PortValueSingle(UpstreamMessage):
    def __init__(self, bytes):
        UpstreamMessage.__init__(self, bytes)
        self._port_id = self.payload_uint8(0)
        self._int32value = self.payload_uint32(1)

    def port_id(self):
        return self._port_id

    def int32value(self):
        return self._int32value

    def __repr__(self):
        return f'Value @ {port_desc(self._port_id)}: {self._int32value}'


##################################################################################################
# Port output
##################################################################################################


class PORT_OUTPUT_SUBCOMMAND:
    WRITE_DIRECT = 0x50
    WRITE_DIRECT_MODE_DATA = 0x51
    MOTOR_START_POWER = 0x01
    MOTOR_SET_ACC_TIME = 0x05
    MOTOR_SET_DEC_TIME = 0x06
    MOTOR_START_SPEED = 0x07
    MOTOR_START_SPEED_FOR_TIME = 0x09
    MOTOR_START_SPEED_FOR_DEGREES = 0x0B

class MOTOR_END_STATE:
    FLOAT = 0
    HOLD = 126
    BRAKE = 127

class PortOutput(DownstreamMessage):
    FLAG_EXECUTE_IMMEDIATELY = 0b00000001
    FLAG_FEEDBACK = 0b00010000

    def __init__(self, port, subcommand, flags = FLAG_EXECUTE_IMMEDIATELY):
        DownstreamMessage.__init__(self, MessageTypeIds.PORT_OUTPUT)
        self._port_id = port
        self._subcommand = subcommand
        self._flags = flags        

    def get_payload(self):
        return self.to_uint8(self._port_id) + self.to_uint8(self._flags) + self.to_uint8(self._subcommand) + self.get_sub_payload()

    def get_sub_payload(self):
        raise "Not implemented"


    def __repr__(self):
         return f'Output to port {port_desc(self._port_id)}:  {value_name(PORT_OUTPUT_SUBCOMMAND, self._subcommand)}: {self.get_sub_payload()}'

class PortOutputFeedback(UpstreamMessage):
    def __init__(self, bytes):
        UpstreamMessage.__init__(self, bytes)
        self._port_id = self.payload_uint8(0)
        self._message = self.payload_uint8(1)

    def port_id(self):
        return self._port_id

    def message(self):
        msgs = []
        if self._message & 0x01:
            msgs.append("Buffer empty + command in progress")
        if self._message & 0x02:
            msgs.append("Buffer empty + command completed")
        if self._message & 0x04:
            msgs.append("Current command(s) discarded")
        if self._message & 0x08:
            msgs.append("Idle")
        if self._message & 0x10:
            msgs.append("Busy / full")
        return ", ".join(msgs)

    def is_completed(self):
        return self._message & 0x02

    def __repr__(self):
        return f'Feedback for output to port {port_desc(self._port_id)}: {self._message}: {self.message()}'


class SetRgbColor(PortOutput):
    def __init__(self, port, r, g, b):
        PortOutput.__init__(self, port, PORT_OUTPUT_SUBCOMMAND.WRITE_DIRECT_MODE_DATA)
        self.r = r
        self.g = g
        self.b = b

    def get_sub_payload(self):
        return self.to_uint8(0x01) + self.to_uint8(self.r) + self.to_uint8(self.g) + self.to_uint8(self.b)

    def __repr__(self):
        return f'RGB output to port {port_desc(self._port_id)}: R:{self.r} G:{self.g} B:{self.b}'

class MotorStartPower(PortOutput):
    def __init__(self, port_id, power):
        PortOutput.__init__(self, port_id, PORT_OUTPUT_SUBCOMMAND.MOTOR_START_POWER)
        self._power = power

    def get_sub_payload(self):
        return self.to_int8(self._power)    

    def __repr__(self):
        return f'Start power to motor @ {port_desc(self._port_id)}: {self._power}'

class MotorBrake(MotorStartPower):
    def __init__(self, port_id):
        MotorStartPower.__init__(self, port_id, 127)

    def __repr__(self):
        return f'Brake motor @ {port_desc(self._port_id)}'


class MotorSetAccTime(PortOutput):
    def __init__(self, port_id, acc_time_ms, profile_id=0):
        PortOutput.__init__(self, port_id, PORT_OUTPUT_SUBCOMMAND.MOTOR_SET_ACC_TIME)
        self._acc_time_ms = acc_time_ms
        self._profile_id = profile_id

    def get_sub_payload(self):
        return self.to_int16(self._acc_time_ms) + self.to_int8(self._profile_id)

    def __repr__(self):
        return f'Set motor acc profile #{self._profile_id} @ {port_desc(self._port_id)}: {self._acc_time_ms} from 0% to 100%'


class MotorSetDecTime(PortOutput):
    def __init__(self, port_id, dec_time_ms, profile_id=0):
        PortOutput.__init__(self, port_id, PORT_OUTPUT_SUBCOMMAND.MOTOR_SET_DEC_TIME)
        self._dec_time_ms = dec_time_ms
        self._profile_id = profile_id

    def get_sub_payload(self):
        return self.to_int16(self._dec_time_ms) + self.to_int8(self._profile_id)

    def __repr__(self):
        return f'Set motor dec profile #{self._profile_id} @ {port_desc(self._port_id)}: {self._dec_time_ms} from 100% to 0%'


class MotorStartSpeed(PortOutput):
    def __init__(self, port_id, speed, max_power=100, use_profile=0b11):
        PortOutput.__init__(self, port_id, PORT_OUTPUT_SUBCOMMAND.MOTOR_START_SPEED)
        self._speed = speed
        self._max_power = max_power
        self._use_profile = use_profile

    def get_sub_payload(self):
        return self.to_int8(self._speed) + self.to_int8(self._max_power) + self.to_int8(self._use_profile)

    def __repr__(self):
        return f'Start motor @ {port_desc(self._port_id)} at speed {self._speed}'


class MotorStop(MotorStartSpeed):
    def __init__(self, port_id, use_profile=0b11):
        MotorStartSpeed.__init__(self, port_id, 0, use_profile=use_profile)

    def __repr__(self):
        return f'Stop motor @ {port_desc(self._port_id)}'

class MotorStartSpeedForTime(PortOutput):
    def __init__(self, port_id, speed, time_ms, max_power=100, use_profile=0b11):
        PortOutput.__init__(self, port_id, PORT_OUTPUT_SUBCOMMAND.MOTOR_START_SPEED)
        self._speed = speed
        self._time_ms = time_ms
        self._max_power = max_power
        self._use_profile = use_profile

    def get_sub_payload(self):
        return self.to_int16(self._time_ms) + self.to_int8(self._speed) + self.to_int8(self._max_power) + self.to_int8(self._use_profile)

    def __repr__(self):
        return f'Start motor @ {port_desc(self._port_id)} at speed {self._speed} for {self._time_ms} ms'


class MotorStartSpeedForDegrees(PortOutput):
    def __init__(self, port_id, degrees, speed, max_power=100, end_state=127, use_profile=0b00):
        PortOutput.__init__(self, port_id, PORT_OUTPUT_SUBCOMMAND.MOTOR_START_SPEED_FOR_DEGREES)
        self._speed = speed
        self._degrees = degrees
        self._max_power = max_power
        self._end_state = end_state
        self._use_profile = use_profile

    def get_sub_payload(self):
        return self.to_int32(self._degrees) + self.to_int8(self._speed) + self.to_int8(self._max_power) + self.to_int8(self._end_state) + self.to_int8(self._use_profile)

    def __repr__(self):
        return f'Start motor @ {port_desc(self._port_id)} at speed {self._speed} for {self._degrees} degrees'

##################################################################################################

def decode_upstream_message(bytes):
    msg_type = as_int(bytes[2:3])
    if msg_type == MessageTypeIds.HUB_PROPERTIES:
        return PropertyUpdate(bytes)
    elif msg_type == MessageTypeIds.HUB_ATTACHED_IO:
        return AttachedIO(bytes)
    elif msg_type == MessageTypeIds.HUB_ERROR:
        return HubError(bytes)
    elif msg_type == MessageTypeIds.PORT_INPUT_FORMAT_SINGLE:
        return PortInputFormatSingle(bytes)
    elif msg_type == MessageTypeIds.PORT_OUTPUT_FEEDBACK:
        return PortOutputFeedback(bytes)
    elif msg_type == MessageTypeIds.PORT_VALUE_SINGLE:
        return PortValueSingle(bytes)
    else:
        return UpstreamMessage(bytes)

def port_desc(port_id):
    if is_port_internal(port_id):
        return f"internal({port_id})"
    else:
        return ['A', 'B', 'C', 'D', 'E', 'F'][port_id]            

def is_port_internal(port_id):
    return port_id >= 50        

def value_name(clazz, val):
    obj = clazz()
    for attr in dir(obj):
        if getattr(obj, attr) == val:
            return attr
    return f"UNKNOWN[0x{hex(val)}]"