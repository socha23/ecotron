import glob
from sound import Clip
from value_source import Concat, FadeOut, GradientDefinition, GradientWalk, Progression, ValueSource, RGB, repeated_pulse, Multiply, repeated_pulse, Constant
import random

ELECTRICITY_ZAP_CLIPS = [Clip(path) for path in glob.glob("./resources/electric_zap_*.ogg")]
ELECTRICITY_SHOCK_CLIPS = [Clip(path) for path in glob.glob("./resources/electric_shock_*.ogg")]


EXPLOSION_GRADIENT = GradientDefinition([
    (0, RGB(0, 0, 0)),
    (0.15, RGB(160, 0, 0)),
    (0.35, RGB(255, 0, 0)),
    (0.7, RGB(255, 100, 0)),
    (1, RGB(255, 200, 50)),
])

PHASE_1_DURATION = 1
PHASE_1_FORCE = [0.5, 0.8]
PHASE_1_TIME = [0.1, 0.2]

PHASE_2_DURATION = 2
PHASE_2_FORCE = [0.3, 0.6]
PHASE_2_TIME = [0.1, 0.5]

FADEOUT_TIME = 3

CLIP_BOOM = Clip("./resources/explosion_large_1.ogg")


class ExplosionSource(ValueSource):
    def __init__(self
    ):
        super().__init__()
        self._current_flame_source = None
        self._fadeout_source = FadeOut(FADEOUT_TIME, self._current_flame_source)
        self._start_time = self.current_time()
        self._next_flame()

    def value(self):
        if self._current_flame_source.is_finished():
            self._next_flame()
        return self._fadeout_source.value()

    def is_finished(self):
        return self._fadeout_source.is_finished()

    def _next_flame(self):
        force = 0
        time = 0

        time_elapsed = self.current_time() - self._start_time

        if (time_elapsed > PHASE_1_DURATION + PHASE_2_DURATION
                and not self._fadeout_source.is_fading_out()):
            self._fadeout_source.fadeout()


        if time_elapsed < PHASE_1_DURATION:
            force = random.uniform(*PHASE_1_FORCE)
            time = random.uniform(*PHASE_1_TIME)
        else:
            force = random.uniform(*PHASE_2_FORCE)
            time = random.uniform(*PHASE_2_TIME)
        val_source = repeated_pulse(1, time, Constant(force))
        self._current_flame_source = GradientWalk(EXPLOSION_GRADIENT, val_source)
        self._fadeout_source._inner_source = self._current_flame_source


def explosion_now(px_size, stereo=[1, 1]):
    CLIP_BOOM.play(stereo=stereo)
    return Progression(
        repeated_pulse(1, 0.2),
        Multiply(
            Constant(0.5),
            Concat(*[ExplosionSource() for _ in range(px_size)])
        )
    )
