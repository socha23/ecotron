from digitalio import Direction, Pull
from tick_aware import TickAware, TickAwareController

#encoder_controller = TickAwareController(tick_time = 0.001)
#encoder_controller.on = True

class Encoder(TickAware):

    TRANSITION_CLOCKWISE =  ((False, False), (False, True), (True, True))
    TRANSITION_COUNTER_CLOCKWISE = ((True, True), (False, True), (False, False))

    def __init__(self, pin_a, pin_b):                
        #TickAware.__init__(self, controller=encoder_controller)
        TickAware.__init__(self)
        self._pin_a = pin_a
        self._pin_b = pin_b

        self.on_change = lambda sign: None

        pin_a.direction = Direction.INPUT
        pin_a.pull = Pull.UP
        
        pin_b.direction = Direction.INPUT
        pin_b.pull = Pull.UP

        self._last_value_2 = (False,False)
        self._last_value_1 = (False,False)

    @property
    def value(self):
        return self._last_value_1

    def tick(self, time, delta):
        #print(f"tick at {self.current_time()}")
        new_value = (self._pin_a.value, self._pin_b.value)
        if new_value != self._last_value_1:
            if (self._last_value_2, self._last_value_1, new_value) == Encoder.TRANSITION_CLOCKWISE:
                if self.on_change:
                    self.on_change(1)
            elif (self._last_value_2, self._last_value_1, new_value) == Encoder.TRANSITION_COUNTER_CLOCKWISE:
                if self.on_change:
                    self.on_change(-1)

            self._last_value_2 = self._last_value_1
            self._last_value_1 = new_value
            
