from director import Script
import value_source
from value_source import RGB
from sound import Clip
import math
import effects.electricity
from ecotron.widget import Widget


class Hyperscanner(Widget):
    CLIP_DING = Clip("./resources/microwave_ding1.ogg", volume=0.1)

    STATUS_INDICATOR_SCALING = 0.25

    def __init__(self, inner_neopixel, status_neopixel, director):
      Widget.__init__(self)
      self._inner_neopixel = inner_neopixel
      self._status_neopixel = status_neopixel
      self._director = director
      self._current_script_runner = None

    def _status_busy(self, duration_s=None):
        WAVE_DURATION = 1.5

        source = self._scale_status(
            value_source.Sine(WAVE_DURATION, value_source.RGB(237, 64, 20), common_phase=False)
            )
        if duration_s != None:
            source = value_source.TimeConstrained(math.floor(duration_s / WAVE_DURATION) * WAVE_DURATION, source)
        self._status_neopixel.source = source

    def _status_success(self, duration_s=None):
        Hyperscanner.CLIP_DING.play()
        self._status_neopixel.source = value_source.repeated_pulse(3, 0.5, self._scale_status(value_source.RGB(0, 255, 0)))

    def when_turn_on(self):
        self._inner_neopixel.source = value_source.AlwaysOff()
        self._status_off()

    def when_turn_off(self):
        self._inner_neopixel.source = value_source.AlwaysOff()
        self._status_off()
        if self._current_script_runner:
          self._current_script_runner.cancel()
          self._current_script_runner = None

    def _status_off(self):
        self._status_neopixel.source = value_source.AlwaysOff()

    def _scale_status(self, source):
        return value_source.Multiply(source, value_source.Constant(Hyperscanner.STATUS_INDICATOR_SCALING))

    def _reset_current_script_runner(self):
      self._current_script_runner = None

    def run_scan_cycle(self, duration=5):
      if not self.on:
        return
      PHASE_0_TIME = 0.5
      PHASE_2_TIME = 1
      PHASE_3_TIME = 0.5
      BUSY_TIME = max(0, duration - PHASE_0_TIME - PHASE_2_TIME - PHASE_3_TIME)

      s = (Script()
          .add_sleep(PHASE_0_TIME)
          .add_step(lambda: self._status_busy(BUSY_TIME))
      #    .add(_ultraviolet_script(hyperscanner, BUSY_TIME))
          .add(effects.electricity.zap_script(self._inner_neopixel, BUSY_TIME))
          .add_sleep(PHASE_2_TIME)
          .add_step(self._status_success)
          .add_step(self._reset_current_script_runner)
      )
      self._current_script_runner = self._director.execute(s)


#def _ultraviolet_script(hyperscanner, duration_s=5):
#    return (Script().add_step(lambda:
#        hyperscanner.run_inner_source(
#            value_source.Multiply(
#                value_source.Constant(0.3),
#                value_source.Flicker(0.2,
#                    value_source.Gradient(duration_s, [
#                        (0, RGB(0, 0, 0)),
#                        (0.2, RGB(101, 0, 194)),
#                        (0.5, RGB(140, 31, 240)),
#                        (0.7, RGB(86, 18, 148)),
#                        (0.9, RGB(73, 0, 140)),
#                        (1, RGB(0, 0, 0))
#                    ])
#                )
#            )
#    )).add_sleep(duration_s))

