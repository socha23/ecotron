COLOR_STEP = 0.02

class ColorController:

    def __init__(self):
        self._current_property = None


    def set_current_property(self, property):
        self._current_property = property

    def change_red(self, sign):
        self._change_color(sign * COLOR_STEP, 0, 0)

    def change_green(self, sign):
        self._change_color(0, sign * COLOR_STEP, 0)

    def change_blue(self, sign):
        self._change_color(0, 0, sign * COLOR_STEP)

    def _change_color(self, d_r, d_g, d_b):
        if not self._current_property:
            return
        r, g, b = self._current_property.value()
        r = max(0, min(1, r + d_r))
        g = max(0, min(1, g + d_g))
        b = max(0, min(1, b + d_b))

        print(f"color changed to {r, g, b}")

        self._current_property.set_value((r, g, b))

DEFAULT_COLOR_CONTROLLER = ColorController()
