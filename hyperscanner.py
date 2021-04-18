from director import Script
import value_source
import math

class Hyperscanner:
    
    STATUS_INDICATOR_SCALING = 0.25

    def __init__(self, inner_neopixel, status_neopixel):
        self._inner_neopixel = inner_neopixel
        self._status_neopixel = status_neopixel
    

    def status_busy(self, duration_s=None):
        WAVE_DURATION = 1.5

        source = self._scale_status(
            value_source.Sine(WAVE_DURATION, value_source.RGB(237, 192, 43), common_phase=False)
            )
        if duration_s != None:
            source = value_source.TimeConstrained(math.floor(duration_s / WAVE_DURATION) * WAVE_DURATION, source)
        self._status_neopixel.source = source

    def status_success(self, duration_s=None):
        self._status_neopixel.source = value_source.repeated_blink(3, 0.5, self._scale_status(value_source.RGB(0, 255, 0)))

    def run_gradient(self, gradient_defition, duration_s=3):
        self._inner_neopixel.source = value_source.Gradient(duration_s, gradient_defition)

    def off(self):
        self._inner_neopixel.source = value_source.AlwaysOff()
        self.status_off()

    def status_off(self):
        self._status_neopixel.source = value_source.AlwaysOff()


    def _scale_status(self, source):
        return value_source.Multiply(source, value_source.Constant(Hyperscanner.STATUS_INDICATOR_SCALING))


def scan_cycle_script(hyperscanner, duration=5):

    # 0. wait a little bit
    # 1. display busy on status as long as possible
    # 2. wait a bit
    # 3. display success
    
    PHASE_0_TIME = 0.5
    PHASE_2_TIME = 1.5
    PHASE_3_TIME = 2
    BUSY_TIME = max(0, duration - PHASE_0_TIME - PHASE_2_TIME - PHASE_3_TIME)

    s = (Script()
        .add_sleep(PHASE_0_TIME)
        .add_step(lambda: hyperscanner.status_busy(BUSY_TIME))
        .add_sleep(BUSY_TIME)
        .add_sleep(PHASE_2_TIME)
        .add_step(hyperscanner.status_success)
        .add_sleep(PHASE_3_TIME)
    )
    return s

    