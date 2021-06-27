from ecotron.widget import Widget

class Fans(Widget):

    FAN_SPEED = -0.1

    def __init__(self, motor):
        Widget.__init__(self)
        self._motor = motor
        self._motor.brake()
        self._motor.set_acc_time(10)

    def when_turn_on(self):
        self._motor.start_speed(Fans.FAN_SPEED)

    def when_turn_off(self):
        self._motor.brake()