class Elevator:

    def __init__(self, motor):
        self._motor = motor

    def move(self, position):
        self._motor.goto_absolute_position(position, 0.1, on_completed=self._move_completed)    

    def reset(self):
        self._motor.set_acc_time(0)
        self._motor.set_dec_time(0)
        self._motor.reset_position(0)
        #self._motor.goto_absolute_position(-3500, 0.2, on_completed=self._reset_move_completed)

#        self._motor.start_speed_for_time(-0.2, 5, 
        #on_completed=self._reset_move_completed)    

    def _reset_move_completed(self):
        self._motor.reset_position(0)
        self._move_completed()

    def _move_completed(self):
        print(f"Move completed at pos {self._motor.position()}")

    def stop(self):
        self._motor.brake()

