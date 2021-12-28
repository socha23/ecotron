from sound import Clip

STATE_OFF = 0
STATE_WARNING = 1
STATE_DANGER = 2

CLIP_WARNING = Clip("./resources/siren_warning.ogg")

WARNING_CLIP_LENGTH = 0.741 # two pulses
WARNING_CLIP_PULSE_LENGTH = WARNING_CLIP_LENGTH / 2

CLIP_DANGER = Clip("./resources/siren_danger.ogg")

DANGER_CLIP_LENGTH = 2.892 # two pulses
DANGER_CLIP_PULSE_LENGTH = DANGER_CLIP_LENGTH / 2


FADE_IN = 0
FADE_OUT = 0.5

class Siren:
    def __init__(self):
        self._state = STATE_OFF
        self._clip = None

    def warning(self, clip=CLIP_WARNING):
        self._state_transition_to(STATE_WARNING, clip)

    def danger(self, clip=CLIP_DANGER):
        self._state_transition_to(STATE_DANGER, clip)

    def off(self):
        self._state_transition_to(STATE_OFF)

    def _state_transition_to(self, state, clip=None):
        if self._state == state:
            return
        self._state = state
        if self._clip:
            self._clip.fadeout(FADE_OUT)
            self._clip = None
        if clip:
            self._clip = clip
            self._clip.loop(fadein=FADE_IN)


DEFAULT = Siren()
