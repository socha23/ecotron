from powered_up.messages import SetRgbColor, IOTypeIds, MotorSetAccTime, MotorSetDecTime, MotorStartPower, MotorStartSpeed, \
    MotorStop, MotorBrake, MotorStartSpeedForTime, MotorStartSpeedForDegrees, PortOutputFeedback, PortValueSingle, PortValueRequest, \
    MotorGotoAbsolutePosition, MotorPresetPosition

from time import sleep

class FakePort:
    def send(self, command):
        pass

    def set_mode(self, mode):
        pass

    def port_id(self):
        return 0


class RGBLED:

    MODE_RGB = 1

    def __init__(self, port=FakePort()):
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
        self._port.set_mode(self.MODE_RGB)

        r, g, b = self.value
        self._port.send(SetRgbColor(self._port.port_id(), r, g, b))

    def set_rgb(self, r, g, b):
        self.value = (r, g, b)

    def is_connected(self):
        return not isinstance(self._port, FakePort)


class Motor:

    MODE_ANGLE_SENSOR = 0x02

    def __init__(self, port=FakePort()):
        self._on_complete = lambda: None
        self._motor_pos = None
        self._logical_pos = 0
        self._logical_pos_delta = None
        self.set_port(port)
        self._command_in_progress = False
        self.on_position_changed = lambda _: None
        self._feedback_mode = False

    def set_port(self, port):
        self._port = port

    def set_feedback_mode(self, delta_interval=1):
        self._feedback_mode = True
        self._port.set_mode(self.MODE_ANGLE_SENSOR, delta_interval, True)
        self._port.send(PortValueRequest(self._port.port_id()))


    def is_initialized(self):
        return self._feedback_mode == False or self._motor_pos != None

    def set_acc_time(self, acc_time_s):
        self._port.send(MotorSetAccTime(self._port.port_id(), acc_time_s * 1000))

    def set_dec_time(self, dec_time_s):
        self._port.send(MotorSetDecTime(self._port.port_id(), dec_time_s * 1000))

    def brake(self, on_complete=None):
        self._on_complete = on_complete
        self._port.send(MotorBrake(self._port.port_id()))

    def start_speed(self, speed, power=1, on_complete=None, execute_immediately=False):
        self._on_complete = on_complete
        self._port.send(MotorStartSpeed(self._port.port_id(), int(speed * 100), max_power=int(power * 100), execute_immediately=execute_immediately))

    def start_speed_for_time(self, speed, time_s, power=1, on_complete=None):
        self._on_complete = on_complete
        self._port.send(MotorStartSpeedForTime(self._port.port_id(), int(speed * 100), time_s * 1000, max_power=int(power * 100)))

    def start_speed_for_degrees(self, speed, degrees, power=1, on_complete=None):
        self._on_complete = on_complete
        self._port.send(MotorStartSpeedForDegrees(self._port.port_id(), int(degrees), int(speed * 100), max_power=int(power * 100)))

    def goto_absolute_position(self, position, speed=1, power=1, on_complete=None, execute_immediately=False):
        self._on_complete = on_complete
        dest_position = position
        if self._logical_pos_delta != None:
            dest_position -= self._logical_pos_delta
        self._port.send(MotorGotoAbsolutePosition(self._port.port_id(), int(dest_position), int(speed * 100), max_power=int(power * 100), execute_immediately=execute_immediately))


    def is_busy(self):
        return self._command_in_progress

    def _on_idle(self):
        if self._command_in_progress:
            self._command_in_progress = False
            if self._on_complete != None:
                self._on_complete()
                self._on_complete = None

    def _on_command_in_progress(self):
        self._command_in_progress = True

    def _on_motor_pos(self, motor_pos):
        self._motor_pos = motor_pos
        if self._logical_pos_delta == None:
            self._logical_pos_delta = self._logical_pos - self._motor_pos
        self._logical_pos = motor_pos + self._logical_pos_delta
        if self.on_position_changed != None:
            self.on_position_changed(self._logical_pos)

    def position(self):
        return self._logical_pos

    def reset_position(self, position=0):
        if self._feedback_mode == True:
            while self._motor_pos == None:
                sleep(0.1)
        if self._feedback_mode == False and self._motor_pos == None:
            self._motor_pos = 0

        self._logical_pos = position
        self._logical_pos_delta = position - self._motor_pos

    def on_upstream_message(self, msg):
        if isinstance(msg, PortOutputFeedback):
            #print(f"got output feedback: {msg} at pos:{self._logical_pos}")
            pass
        if isinstance(msg, PortOutputFeedback) and msg.is_in_progress():
            self._on_command_in_progress()
        if isinstance(msg, PortOutputFeedback) and msg.is_idle():
            self._on_idle()
        if isinstance(msg, PortValueSingle):
            self._on_motor_pos(msg.int32value())


def instantiate_device(device_id, port):
    if device_id == IOTypeIds.EXTERNAL_MOTOR_TACHO:
        return Motor(port)
