from ecotron.properties import LightMode
from speech import say, SpeechLines

COLOR_STEP = 0.02
PARAM_STEP = 0.1

MODES = [LightMode.CONSTANT, LightMode.PULSE, LightMode.PLASMA]
LINES = {
    LightMode.CONSTANT: SpeechLines.COLOR_MODE_CONSTANT,
    LightMode.PULSE: SpeechLines.COLOR_MODE_PULSE,
    LightMode.PLASMA: SpeechLines.COLOR_MODE_PLASMA
}

class ColorController:

    def __init__(self):
        self._props = None


    def set_current_properties(self, properties):
        self._props = properties

    def change_red(self, sign):
        self._change_color(sign * COLOR_STEP, 0, 0)

    def change_green(self, sign):
        self._change_color(0, sign * COLOR_STEP, 0)

    def change_blue(self, sign):
        self._change_color(0, 0, sign * COLOR_STEP)

    def change_x(self, sign):
        self.change_mode(sign)

    def change_y(self, sign):
        self._change_param(sign * PARAM_STEP)



    def change_mode(self, sign):
        if not self._props:
            return
        old_mode = self._props.mode.value()
        old_mode_idx = MODES.index(old_mode)
        new_mode_idx = (old_mode_idx + sign) % len(MODES)
        new_mode = MODES[new_mode_idx]

        self._props.mode.set_value(new_mode)
        self._props.param.set_value(0.5)
        if new_mode in LINES:
            say(LINES[new_mode])
        else:
            print(f"No speech line for color mode {new_mode}")

    def _change_param(self, d_v):
        if not self._props:
            return
        old_val = self._props.param.value()
        new_val = max(0, min(1, old_val + d_v))
        if old_val != new_val:
            self._props.param.set_value(new_val)


    def _change_color(self, d_r, d_g, d_b):
        if not self._props:
            return
        r, g, b = self._props.color.value()
        r = max(0, min(1, r + d_r))
        g = max(0, min(1, g + d_g))
        b = max(0, min(1, b + d_b))
        print(f"color changed to {r, g, b}")
        self._props.color.set_value((r, g, b))

DEFAULT_COLOR_CONTROLLER = ColorController()
