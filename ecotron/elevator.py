from components.button import Button
from components.led import LED
from director import Script
from sound import Clip

class ElevatorControls:
    def __init__(self, mcp23017):

        self.floor_buttons = [Button(mcp23017.get_pin(9)), Button(mcp23017.get_pin(11)), Button(mcp23017.get_pin(13))]
        self.floor_button_leds = [LED(mcp23017.get_pin(8)), LED(mcp23017.get_pin(10)), LED(mcp23017.get_pin(12))]
        self.button_green = Button(mcp23017.get_pin(14))
        self.button_red = Button(mcp23017.get_pin(15))


class Elevator:

    STATE_WAITING = 0
    STATE_MOVING = 1

    SPEED = 0.2

    BLINK_TIME = 0.5

    FLOOR_HEIGHTS = [0, 1500, 3000]

    CLIP_DING = Clip("./resources/elevator_ding.ogg", volume=0.5)

    def __init__(self, motor, controls, director):
        self._director = director
        self._motor = motor
        self._current_floor = None
        self._controls = controls
        for floor_idx in range(len(Elevator.FLOOR_HEIGHTS)):
            controls.floor_buttons[floor_idx].on_press = lambda floor_idx=floor_idx: self.go_to_floor(floor_idx)
            controls.floor_button_leds[floor_idx].off()
        
        controls.button_red.on_press = self.go_floor_up
        controls.button_green.on_press = self.go_floor_down
                
        self.reset()


    def go_floor_up(self):
        if self._current_floor < len(Elevator.FLOOR_HEIGHTS):
            self.go_to_floor(self._current_floor + 1)

    def go_floor_down(self):
        if self._current_floor > 0:
            self.go_to_floor(self._current_floor -1)

    def go_to_floor(self, floor_idx):
        if self._state != Elevator.STATE_WAITING:
            return        
        self._director.execute(Script()
            .add_step(lambda: self._on_move_start(floor_idx))
            .add_async_step(lambda callback: self._motor.goto_absolute_position(Elevator.FLOOR_HEIGHTS[floor_idx], Elevator.SPEED, on_complete=callback))
            .add_step(lambda: self._on_move_end(floor_idx))
            .add_async_step(lambda callback: Elevator.CLIP_DING.play(on_complete=callback))
        )

    def _on_move_start(self, floor_idx):
        self._state = Elevator.STATE_MOVING
        self._controls.floor_button_leds[self._current_floor].off()
        self._controls.floor_button_leds[floor_idx].blink(Elevator.BLINK_TIME, Elevator.BLINK_TIME)

    def _on_move_end(self, floor_idx):
        self._controls.floor_button_leds[floor_idx].on()
        self._current_floor = floor_idx
        self._state = Elevator.STATE_WAITING

    def reset(self):
        self._motor.set_acc_time(0)
        self._motor.set_dec_time(0)
        self._motor.reset_position(0)
        self._director.execute(Script()
            .add_async_step(lambda callback: self._motor.goto_absolute_position(-3000, 0.5, on_complete=callback))
            .add_step(lambda: self._motor.reset_position(0))
            .add_step(lambda: self._on_move_end(0))
        )
        