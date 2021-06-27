from components.button import Button
from components.led import LED
from director import Script
from sound import Clip

from value_source import ValueSource, RGB, multiply, add, Multiply, Add, Wave, Concat, RepeatedConstant, Max, Constant, FadeInFadeOut


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

    FLOOR_HEIGHTS = [0, 750, 2000]

    ZERO_POSITION = -80

    CLIP_DING = Clip("./resources/elevator_ding2.ogg")
    CLIP_DOOR = Clip("./resources/elevator_door1.ogg", volume=0.6)

    def __init__(self, director, controls, motor, neopixels, ecotron_properties):

        self._director = director
        self._motor = motor
        self._neopixels = neopixels
        self._current_floor = None
        self._current_target = None
        self._queued_floors = []
        self._controls = controls

        self._motor.set_feedback_mode(10)

        self.reset()

        neopixels.source = ElevatorLightStripValueSource(neopixels.size(), self._motor, ecotron_properties.elevator_lights_on)

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
            add_reset_pos = False
            
            dst_pos = Elevator.FLOOR_HEIGHTS[floor_idx]
            if floor_idx == 0:
                add_reset_pos = True
                dst_pos = Elevator.ZERO_POSITION

            script = (Script()
                .add_step(lambda: self._on_move_start(floor_idx))
                .add_async_step(lambda callback: Elevator.CLIP_DOOR.play(on_complete=callback))
                .add_step(lambda: self._neopixels.source.on_move_start(self._current_floor, floor_idx))
                .add_async_step(lambda callback: self._motor.goto_absolute_position(dst_pos, Elevator.SPEED, on_complete=callback))
                .add_step(lambda: self._on_move_end(floor_idx))
            )
            if add_reset_pos:
                script.add_step(lambda:self._motor.reset_position(0))


            (script
                .add_async_step(lambda callback: Elevator.CLIP_DING.play(on_complete=callback))
                .add_step(self._next_queued_floor))

            self._director.execute(script)

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
        self._neopixels.source.on_move_end()

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



class ElevatorLightStripValueSource(ValueSource):

    def __init__(self, size, motor, lights_on_property, pos_per_px=240, height=3):
        ValueSource.__init__(self)

        self._position_value_source = ElevatorPositionValueSource(size, motor, pos_per_px, height)
        self._movement_source = ElevatorMovementValueSource(size, height, 0.1, 0.3)

        self._position_fade = FadeInFadeOut(0.5)
        self._movement_fade = FadeInFadeOut(0.5, False)

        self._inner_source = Max(
            Multiply(self._position_fade, self._position_value_source, RGB(0, 50, 0), lights_on_property),
            Multiply(self._movement_fade, self._movement_source, RGB(0, 64, 64), lights_on_property)
        )

    def value(self):
        return self._inner_source.value()

    def on_move_start(self, from_floor=0, to_floor=0):
        self._movement_source.set_movement(from_floor, to_floor)
        self._position_fade.fade_out()
        self._movement_fade.fade_in()

    def on_move_end(self):
        self._position_fade.fade_in()
        self._movement_fade.fade_out()


class ElevatorMovementValueSource(ValueSource):

    def __init__(self, size, height=1, intensity_from=0, intensity_to=1):        
        ValueSource.__init__(self)
        self._height = height
        self._size = size
        self.set_movement(0, 0)
        self._intensity_from = intensity_from
        self._intensity_to = intensity_to
        

    def set_movement(self, from_floor=0, to_floor=0):

        FLOOR_LED_IDX = [0, 4, 10]

        if from_floor == to_floor:
            self._inner_source = RepeatedConstant(0, self._size)
            return

        downmost = FLOOR_LED_IDX[min(from_floor, to_floor)]
        upmost = min(self._size, FLOOR_LED_IDX[max(from_floor, to_floor)] + self._height)

        partials = []
        if downmost > 0:
            partials.append(RepeatedConstant(0, downmost))

        pixels_per_s = 10 if from_floor < to_floor else -10

        partials.append(
            Add(
                Constant(self._intensity_from),
                Multiply(
                    Wave(upmost - downmost, pixels_per_s=pixels_per_s, wave_width=1, spread=4),
                    Constant(self._intensity_to - self._intensity_from)
                )                
            )            
        )

        if upmost < self._size:
            partials.append(RepeatedConstant(0, self._size - upmost))

        self._inner_source = Concat(*partials)

    def value(self):
        return self._inner_source.value()


class ElevatorPositionValueSource(ValueSource):

    def __init__(self, size, motor, pos_per_px=230, height=1):
        ValueSource.__init__(self)
        self._size = size
        self._motor = motor
        self._pos_per_px = pos_per_px
        self._height = height

    def value(self):
        motor_pos_px = max(0, self._motor.position()) / self._pos_per_px
        result = []
        for i in range(self._size):
            if i < motor_pos_px - 1:
                result.append(0)
            elif i < motor_pos_px :
                result.append(1 + i - motor_pos_px)
            elif i < motor_pos_px + self._height:
                result.append(1)
            elif i < motor_pos_px + self._height + 1:
                result.append(motor_pos_px + self._height + 1 - i)
            else:
                result.append(0)
        return result


