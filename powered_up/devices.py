from powered_up.messages import SetRgbColor, IOTypeIds, MotorSetAccTime, MotorSetDecTime, MotorStartPower, MotorStartSpeed, \
    MotorStop, MotorBrake, MotorStartSpeedForTime, MotorStartSpeedForDegrees, PortOutputFeedback, PortValueSingle, PortValueRequest

class RGBLED:

    MODE_RGB = 1

    def __init__(self, port=None):
        self._port = port
        self._value = None

    def set_port(self, port):
        self._port = port
        if self.value != None:
            self._send_rgb_commands()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val
        self._send_rgb_commands()

    def _send_rgb_commands(self):
        if self._port == None:
            return
        self._port.set_mode(self.MODE_RGB)    
        
        r, g, b = self.value
        self._port.send(SetRgbColor(self._port.port_id(), r, g, b))    
    
    def set_rgb(self, r, g, b):
        self.value = (r, g, b)


class Motor:

    MODE_ANGLE_SENSOR = 0x02

    def __init__(self, port=None):
        self._on_completed = lambda: None
        self.set_port(port)
        self._current_angle = None
        self._wanted_angle = None

    def set_port(self, port):
        self._port = port
        self._port.set_mode(self.MODE_ANGLE_SENSOR, 1, True) 
        self._port.send(PortValueRequest(self._port.port_id()))

    def set_acc_time(self, acc_time_ms):
        if self._port == None:
            return
        self._port.send(MotorSetAccTime(self._port.port_id(), acc_time_ms))
    
    def set_dec_time(self, dec_time_ms):
        if self._port == None:
            return
        self._port.send(MotorSetDecTime(self._port.port_id(), dec_time_ms))

    def brake(self):
        if self._port == None:
            return
        self._port.send(MotorBrake(self._port.port_id()))

    def start_speed(self, speed, power=1):
        if self._port == None:
            return
        self._port.send(MotorStartSpeed(self._port.port_id(), int(speed * 100), max_power=int(power * 100)))

    def start_speed_for_time(self, speed, time_s, power=1):
        if self._port == None:
            return
        self._port.send(MotorStartSpeedForTime(self._port.port_id(), int(speed * 100), time_s * 1000, max_power=int(power * 100)))

    def start_speed_for_degrees(self, speed, degrees, power=1, on_completed = lambda: None):
        if self._port == None:
            return
        self._on_completed = on_completed
        self._wanted_angle += degrees
        degrees_to_move = self._wanted_angle - self._current_angle
        self._port.send(MotorStartSpeedForDegrees(self._port.port_id(), degrees_to_move, int(speed * 100), max_power=int(power * 100)))

    def on_upstream_message(self, msg):
        if isinstance(msg, PortOutputFeedback) and msg.is_completed():
            callback = self._on_completed
            self._on_completed = None
            callback()
        elif isinstance(msg, PortValueSingle):            
            self._current_angle = msg.int32value()            
            if self._wanted_angle == None:
                self._wanted_angle = msg.int32value()
            


def instantiate_device(device_id, port):
    if device_id == IOTypeIds.EXTERNAL_MOTOR_TACHO:
        return Motor(port)