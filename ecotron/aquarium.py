from ecotron.color_controller import DEFAULT_COLOR_CONTROLLER
from ecotron.properties import DEFAULT_ECOTRON_PROPERTIES
from ecotron.xy_controller import DEFAULT_XY_CONTROLLER, XyListener
from typing import ValuesView
from ecotron.widget import Widget
from ecotron.lights import flash_pixels
from value_source import AlwaysOff, RGB, Concat, Constant, Gradient, GradientDefinition, GradientRandomWalk, ModifyColor, Multiply, Negative, clamp

BRIGHTNESS = 0.5

class _AquariumPropsController(XyListener):
    def __init__(self):
        pass

    def when_turn_on(self):
        DEFAULT_XY_CONTROLLER.set_current_listener(self)
        DEFAULT_COLOR_CONTROLLER.set_current_property(DEFAULT_ECOTRON_PROPERTIES.aquarium_color)

    def when_turn_off(self):
        DEFAULT_XY_CONTROLLER.set_current_listener(None)
        DEFAULT_COLOR_CONTROLLER.set_current_property(None)

    def on_x_changed(self, sign):
        pass

    def on_y_changed(self, sign):
        p = DEFAULT_ECOTRON_PROPERTIES.aquarium_hue_drift
        p.set_value(p.value() + sign * 0.02)


class Aquarium(Widget, XyListener):
    def __init__(self, pixel_lines):
        Widget.__init__(self)
        XyListener.__init__(self)
        self._pixel_lines = pixel_lines
        self._props_controller = _AquariumPropsController()

    def when_turn_off(self):
        self._props_controller.when_turn_off()
        for line in self._pixel_lines:
            line.source = AlwaysOff()

    def when_turn_on(self):
        self._props_controller.when_turn_on()
        for idx, line in enumerate(self._pixel_lines):
            inner_source = Concat(*[self._create_px_source(idx, pos) for pos in range(line.size())])
            line.source = Multiply(
                inner_source,
                Constant(BRIGHTNESS)
            )

    def _create_px_source(self, line_idx, col_idx):
        hue_gradient = GradientDefinition([
            (0, Negative(DEFAULT_ECOTRON_PROPERTIES.aquarium_hue_drift)),
            (1, DEFAULT_ECOTRON_PROPERTIES.aquarium_hue_drift),
        ])
        color_source = ModifyColor(
            DEFAULT_ECOTRON_PROPERTIES.aquarium_color,
            hue_source = GradientRandomWalk(hue_gradient, speed=1)
        )
        brightness_gradient = GradientDefinition([
            (0, Constant(0)),
            (1, Constant(1))
        ])
        row_multiplier = [0.1, 0.1, 0.2, 0.3][line_idx]
        return Multiply(
            color_source,
            GradientRandomWalk(brightness_gradient, speed=3),
            Constant(row_multiplier)
        )
