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

    BLINK_TIME_CURRENT_MOVE = 0.5
    BLINK_TIME_ENQUEUED = (0.2, 0.8)

    FLOOR_HEIGHTS = [0, 1500, 3000]

    CLIP_DING = Clip("./resources/elevator_ding2.ogg")

    def __init__(self, director, controls, motor):

        self._director = director
        self._motor = motor
        self._current_floor = None
        self._current_target = None
        self._queued_floors = []
        self._controls = controls

        self.reset()


    def go_floor_up(self):
        if self._last_target() < len(Elevator.FLOOR_HEIGHTS) - 1:
            self.go_to_floor(self._last_target() + 1)

    def go_floor_down(self):
        if self._last_target() > 0:
            self.go_to_floor(self._last_target() - 1)

    def _last_target(self):
        if self._queued_floors:
            return self._queued_floors[-1]
        elif self._current_target:
            return self._current_target
        elif self._current_floor:
            return self._current_floor
        else:
                return 0

    def go_to_floor(self, floor_idx):
        if self._state == Elevator.STATE_WAITING and self._current_floor == floor_idx:
            return        
        elif self._state != Elevator.STATE_WAITING and floor_idx != self._current_target:
            self._enqueue_floor(floor_idx)
        else:
            self._director.execute(Script()
                .add_step(lambda: self._on_move_start(floor_idx))
                .add_async_step(lambda callback: self._motor.goto_absolute_position(Elevator.FLOOR_HEIGHTS[floor_idx], Elevator.SPEED, on_complete=callback))
                .add_step(lambda: self._on_move_end(floor_idx))
                .add_async_step(lambda callback: Elevator.CLIP_DING.play(on_complete=callback))
                .add_step(self._next_queued_floor)
            )

    def _enqueue_floor(self, floor_idx):        
        if floor_idx not in self._queued_floors:
            self._queued_floors.append(floor_idx)
            self._controls.floor_button_leds[floor_idx].blink(Elevator.BLINK_TIME_ENQUEUED)


    def _next_queued_floor(self):
        if not self._queued_floors:
            return
        else:
            floor = self._queued_floors.pop(0)
            self.go_to_floor(floor)

    def _on_move_start(self, floor_idx):
        self._state = Elevator.STATE_MOVING
        self._current_target = floor_idx
        self._controls.floor_button_leds[self._current_floor].off()
        self._controls.floor_button_leds[floor_idx].blink(Elevator.BLINK_TIME_CURRENT_MOVE)

    def _on_move_end(self, floor_idx):
        self._controls.floor_button_leds[floor_idx].on()
        self._current_floor = floor_idx
        self._current_target = None
        self._state = Elevator.STATE_WAITING

    def reset(self):
        for led in self._controls.floor_button_leds:
            led.off() 
        self._motor.set_acc_time(0)
        self._motor.set_dec_time(0)
        self._director.execute(Script()
        #    .add_async_step(lambda callback: self._motor.goto_absolute_position(self._motor.position()-3000, 0.5, on_complete=callback))
            .add_step(lambda: self._motor.reset_position(0))
            .add_step(lambda: self._on_move_end(0))
            )
