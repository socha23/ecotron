from powered_up.messages import SetRgbColor, IOTypeIds, MotorSetAccTime, MotorSetDecTime, MotorStartPower, MotorStartSpeed, \
    MotorStop, MotorBrake, MotorStartSpeedForTime, MotorStartSpeedForDegrees, PortOutputFeedback, PortValueSingle, PortValueRequest, \
    MotorGotoAbsolutePosition, MotorPresetPosition

from tick_aware import TickAware

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


class Motor:

    MODE_ANGLE_SENSOR = 0x02

    def __init__(self, port=FakePort()):
        self._on_completed = lambda: None
        self.set_port(port)
        self._motor_pos = None
        self._logical_pos = 0
        self._logical_pos_delta = None
        self._command_in_progress = False
        self.on_position_changed = lambda _: None

    def set_port(self, port):
        self._port = port
        self._port.set_mode(self.MODE_ANGLE_SENSOR, 1, True) 
        self._port.send(PortValueRequest(self._port.port_id()))        

    def set_acc_time(self, acc_time_s):
        self._port.send(MotorSetAccTime(self._port.port_id(), acc_time_s * 1000))
    
    def set_dec_time(self, dec_time_s): 
        self._port.send(MotorSetDecTime(self._port.port_id(), dec_time_s * 1000))

    def brake(self, on_completed=None):
        self._on_completed = on_completed
        self._port.send(MotorBrake(self._port.port_id()))

    def start_speed(self, speed, power=1, on_completed=None, execute_immediately=False):
        self._on_completed = on_completed
        self._port.send(MotorStartSpeed(self._port.port_id(), int(speed * 100), max_power=int(power * 100), execute_immediately=execute_immediately))

    def start_speed_for_time(self, speed, time_s, power=1, on_completed=None):
        self._on_completed = on_completed
        self._port.send(MotorStartSpeedForTime(self._port.port_id(), int(speed * 100), time_s * 1000, max_power=int(power * 100)))

    def start_speed_for_degrees(self, speed, degrees, power=1, on_completed=None):
        self._on_completed = on_completed
        self._port.send(MotorStartSpeedForDegrees(self._port.port_id(), int(degrees), int(speed * 100), max_power=int(power * 100)))

    def goto_absolute_position(self, position, speed, power=1, on_completed=None, execute_immediately=False):
        self._on_completed = on_completed
        self._port.send(MotorGotoAbsolutePosition(self._port.port_id(), int(position - self._logical_pos_delta), int(speed * 100), max_power=int(power * 100), execute_immediately=execute_immediately))

    def _on_idle(self):
        if True:#self._command_in_progress:
            self._command_in_progress = False
            if self._on_completed != None:                
                self._on_completed()
                self._on_completed = None

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

    def reset_position(self, position):
        self._logical_pos = position
        self._logical_pos_delta = position - self._motor_pos

    def on_upstream_message(self, msg):
        if isinstance(msg, PortOutputFeedback):
            print(f"got output feedback: {msg} at pos:{self._logical_pos}")
        if isinstance(msg, PortOutputFeedback) and msg.is_in_progress():
            self._on_command_in_progress()
        if isinstance(msg, PortOutputFeedback) and msg.is_idle():
            self._on_idle()
        if isinstance(msg, PortValueSingle):            
            self._on_motor_pos(msg.int32value())

class InterruptableMotor(TickAware):

    STATE_WAITING = 0
    STATE_RUNNING = 1
    STATE_BRAKING = 2

    def __init__(self, motor):
        TickAware.__init__(self)
        self._motor = motor
        self._motor.on_position_changed = self._on_motor_pos
        self._on_completed = None
        self._target_pos = 0
        self._speed = 0
        self._state = InterruptableMotor.STATE_WAITING

    def set_acc_time(self, acc_time_s):
        self._motor.set_acc_time(acc_time_s)
    
    def set_dec_time(self, dec_time_s): 
        self._motor.set_dec_time(dec_time_s)

    def goto_absolute_position(self, position, speed, power=1, on_completed = None):
        print(f"goto {position}")
        self._target_pos = position
        self._speed = speed
        self._on_completed = on_completed
        if self._state == InterruptableMotor.STATE_RUNNING:
            self.brake(on_completed=self._start_motor)
        else:
            self._start_motor()

    def _start_motor(self):
        sign = 1 if self._target_pos > self._motor.position() else -1
        print(f"starting speed {sign * self._speed}")
        self._motor.start_speed(sign * self._speed, on_completed=lambda:print("START COMPLETED"), execute_immediately=False)
        self._state = InterruptableMotor.STATE_RUNNING

    def brake(self, on_completed=None):
        self._motor.brake(on_completed)
        self._state = InterruptableMotor.STATE_WAITING

    def reset_position(self, pos):
        self._motor.reset_position(pos)

    def position(self):
        return self._motor.position()

    def braking_distance(self):
        return 200

    def _on_motor_pos(self, motor_pos):
        if self._state == InterruptableMotor.STATE_RUNNING:            
            if abs(self._target_pos - self._motor.position()) < self.braking_distance():
                print(f"BRAKING at {self._motor.position()}")
                self._state = InterruptableMotor.STATE_BRAKING
                self._motor.brake(on_completed=self._on_brake_completed)
    
    def _on_midbrake_completed(self):
        print("BRAKE COMPLETED")


    def _on_brake_completed(self):
        print("BRAKE COMPLETED")

def instantiate_device(device_id, port):
    if device_id == IOTypeIds.EXTERNAL_MOTOR_TACHO:
        return Motor(port)
