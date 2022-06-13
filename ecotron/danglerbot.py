from director import Script


POS_UPDATE_DELTA = 5

MOVE_SPEED = 0.2

FIRST_PLANT_CORRECTION = -20
LAST_PLANT_CORRECTION = 0

POS_PLANT = [0, 140, 260, 360]

ON_TURN_ON_MOVE = -360

class DanglerBot:
    def __init__(self, motor):
        self._motor = motor
        self._current_plant = 0
        self._during_move = True
        (Script()
            .add_step(lambda: motor.set_feedback_mode(POS_UPDATE_DELTA))
            .add_sleep(0.1)
            .add_step(motor.reset_position)
            .add_async_step(lambda c: motor.goto_absolute_position(ON_TURN_ON_MOVE, MOVE_SPEED, on_complete=c))
            .add_step(motor.reset_position)
            .add_step(self._on_finish_move)
        ).execute()

    def _on_finish_move(self):
        self._during_move = False

    def _set_current_plant(self, val):
        self._current_plant = val

    def next_plant(self):
        print("next plant")
        self.move_to_plant(self._current_plant + 1)

    def prev_plant(self):
        print("prev plant")
        self.move_to_plant(self._current_plant - 1)

    def move_to_plant(self, idx):
        idx = max(0, min(len(POS_PLANT), idx))
        if self._during_move or self._current_plant == idx:
            return
        self._during_move = True
        pos = POS_PLANT[idx]
        after_move = lambda: None

        motor = self._motor

        if idx == 0:
            after_move = lambda: motor.reset_position(POS_PLANT[idx])
            pos += FIRST_PLANT_CORRECTION
        elif idx == len(POS_PLANT) - 1:
            after_move = lambda: motor.reset_position(POS_PLANT[idx])
            pos += LAST_PLANT_CORRECTION

        (Script()
            .add_step(lambda: print(f"Move to idx {idx}, pos {pos}"))
            .add_async_step(lambda c: self._motor.goto_absolute_position(
                pos,
                speed=MOVE_SPEED,
                on_complete=c))
            .add_step(after_move)
            .add_step(lambda: self._set_current_plant(idx))
            .add_step(self._on_finish_move)
            .add_step(lambda: print(f"Move finished on pos {motor.position()}"))

        ).execute()
