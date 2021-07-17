from director import Script
import value_source
from value_source import RGB
from sound import Clip
import math
import effects.electricity


class Hyperscanner:
    CLIP_DING = Clip("./resources/microwave_ding1.ogg", volume=0.1)        

    STATUS_INDICATOR_SCALING = 0.25

    def __init__(self, inner_neopixel, status_neopixel):
        self._inner_neopixel = inner_neopixel
        self._status_neopixel = status_neopixel
    

    def status_busy(self, duration_s=None):
        WAVE_DURATION = 1.5

        source = self._scale_status(
            value_source.Sine(WAVE_DURATION, value_source.RGB(237, 64, 20), common_phase=False)
            )
        if duration_s != None:
            source = value_source.TimeConstrained(math.floor(duration_s / WAVE_DURATION) * WAVE_DURATION, source)
        self._status_neopixel.source = source

    def status_success(self, duration_s=None):
        Hyperscanner.CLIP_DING.play()
        self._status_neopixel.source = value_source.repeated_pulse(3, 0.5, self._scale_status(value_source.RGB(0, 255, 0)))

    def run_inner_source(self, source):
        self._inner_neopixel.source = source

    def off(self):
        self._inner_neopixel.source = value_source.AlwaysOff()
        self.status_off()

    def status_off(self):
        self._status_neopixel.source = value_source.AlwaysOff()


    def _scale_status(self, source):
        return value_source.Multiply(source, value_source.Constant(Hyperscanner.STATUS_INDICATOR_SCALING))



def _ultraviolet_script(hyperscanner, duration_s=5):
    return (Script().add_step(lambda: 
        hyperscanner.run_inner_source(
            value_source.Multiply(
                value_source.Constant(0.3),
                value_source.Flicker(0.2,
                    value_source.Gradient(duration_s, [
                        (0, RGB(0, 0, 0)),
                        (0.2, RGB(101, 0, 194)),
                        (0.5, RGB(140, 31, 240)),
                        (0.7, RGB(86, 18, 148)),
                        (0.9, RGB(73, 0, 140)),
                        (1, RGB(0, 0, 0))
                    ])
                )
            )
    )).add_sleep(duration_s))

def _lightning_script(hyperscanner, director, duration_s=5):
    return effects.electricity.zap_script(hyperscanner._inner_neopixel, duration_s)    


def scan_cycle_script(hyperscanner, duration=5):

    # 0. wait a little bit
    # 1. display busy on status as long as possible
    # 2. wait a bit
    # 3. display success
    
    PHASE_0_TIME = 0.5
    PHASE_2_TIME = 1
    PHASE_3_TIME = 0.5
    BUSY_TIME = max(0, duration - PHASE_0_TIME - PHASE_2_TIME - PHASE_3_TIME)



    s = (Script()
        .add_sleep(PHASE_0_TIME)
        .add_step(lambda: hyperscanner.status_busy(BUSY_TIME))
    #    .add(_ultraviolet_script(hyperscanner, BUSY_TIME))
        .add(_lightning_script(hyperscanner, BUSY_TIME))
        .add_sleep(PHASE_2_TIME)
        .add_step(hyperscanner.status_success)
        .add_sleep(PHASE_3_TIME)
    )
    return s

    