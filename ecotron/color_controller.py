from colorsys import hsv_to_rgb, rgb_to_hsv
from ecotron.properties import LightMode
from speech import say, SpeechLines

COLOR_STEP = 0.02
PARAM_STEP = 0.1

HUE_STEP = 0.01
SATURATION_STEP = 0.1
VALUE_STEP = 0.1


MODES = [LightMode.CONSTANT, LightMode.PULSE, LightMode.PLASMA]
LINES = {
    LightMode.CONSTANT: SpeechLines.COLOR_MODE_CONSTANT,
    LightMode.PULSE: SpeechLines.COLOR_MODE_PULSE,
    LightMode.PLASMA: SpeechLines.COLOR_MODE_PLASMA
}

class ColorController:

    def __init__(self, hsv_mode = True):
        self._props = None
        self._hsv_mode = hsv_mode

    def set_current_properties(self, properties):
        self._props = properties

    def change_red(self, sign):
        if self._hsv_mode:
            self._change_hsv(sign * HUE_STEP, 0, 0)
        else:
            self._change_rgb(sign * COLOR_STEP, 0, 0)

    def change_green(self, sign):
        if self._hsv_mode:
            self._change_hsv(0, sign * SATURATION_STEP, 0)
        else:
            self._change_rgb(0, sign * COLOR_STEP, 0)

    def change_blue(self, sign):
        if self._hsv_mode:
            self._change_hsv(0, 0, sign * VALUE_STEP)
        else:
            self._change_rgb(0, 0, sign * COLOR_STEP)

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


    def _change_rgb(self, d_r, d_g, d_b):
        if not self._props:
            return
        r, g, b = self._props.color.value()
        r = max(0, min(1, r + d_r))
        g = max(0, min(1, g + d_g))
        b = max(0, min(1, b + d_b))
        print(f"color changed to {r, g, b}")
        self._props.color.set_value((r, g, b))

    def _change_hsv(self, d_h, d_s, d_v):

        if not self._props:
            return
        r, g, b = self._props.color.value()
        h, s, v = rgb_to_hsv(r, g, b)
        new_h = (h + d_h) % 1
        new_s = clamp((s + d_s))
        new_v = clamp((v + d_v))
        r, g, b = hsv_to_rgb(new_h, new_s, new_v)

        print(f"color changed to {r, g, b}")
        self._props.color.set_value((r, g, b))

def clamp(v):
    return max(0, min(1, v))

DEFAULT_COLOR_CONTROLLER = ColorController()
