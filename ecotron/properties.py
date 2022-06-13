from colorsys import hsv_to_rgb, rgb_to_hsv
from enum import Enum

def rgb(r, g, b):
    return (r / 256, g / 256, b / 256)

def hsv(h, s, v):
    return hsv_to_rgb(h, s, v)

class LightMode(Enum):
    CONSTANT = 0,
    PULSE = 1,
    PLASMA = 2,

DEFAULT_MODE = LightMode.CONSTANT
DEFAULT_PARAM = 0.5

class EcotronProperties:

    def __init__(self):

        self.control_panel_ligths_on = Property("Control panel ligths on", 1)
        self.master_volume = Property("Master volume", 1)
        self.background_sound_on = Property("Background sound on", 0)
        self.conveyor_on = Property("Conveyor on", 0)
        self.fans_on = Property("Fans on", 0)
        self.repair_table_on = Property("Repair table on", 0)
        self.elevator_lights_on = Property("Elevator lights on", 1)

        self.jungle_on = Property("Jungle on", 0)

        self.aquarium_lights_on = Property("Aquarium lights on", 0)
        self.aquarium_color = Property("Aquarium color", (0, 0.85, 1))
        self.aquarium_hue_drift = Property("Aquarium hue drift", 0.16)

        self.reactor_door_open = Property("Reactor door open", 0)
        self.reactor_lights_on = Property("Reactor warning lights on", 0)

        self.laboratory_on = Property("Laboratory on", 0)

        self.light_strip = LightProperties("Floor lights", hsv(0.467, 0.833, 0.234), mode = LightMode.PLASMA)
        self.top_lights_jungle = LightProperties("Top lights jungle", hsv(0.125, 0.667, 0.234))
        self.door_lights = LightProperties("Door lights", hsv(0.625, 0.667, 0.234))
        self.top_lights_floor_1 = LightProperties("Top lights floor 1", hsv(0.125, 0.667, 0.234))
        self.reactor_fan_lights = LightProperties("Reactor fan lights", hsv(0.0, 1.0, 0.996))
        self.laboratory_top_lights = LightProperties("Laboratory top lights", hsv(0.105, 0.767, 0.469))
        self.laboratory_stalker_lights = LightProperties("Laboratory stalker lights", hsv(0.922, 0.8, 0.7), mode = LightMode.PLASMA)
        self.laboratory_tentacle_lights = LightProperties("Laboratory tentacle plant lights", hsv(0.0, 0.9, 1), mode = LightMode.PLASMA)


    def print_properties(self):
        print()
        for name, val in self.__dict__.items():
            if isinstance(val, LightProperties):
                print(f"self.{name} = {repr(val)}")
        print()



class Property:
    def __init__(self, name="unnamed property", initial_value=None):
        self._value = initial_value
        self._before_first_set = True
        self.on_value_change = lambda x: None
        self._name = name

    def _on_value_change(self):
        self.on_value_change(self.value())
        print(f"{self._name} set to {self.value()}")

    def value(self):
        return self._value

    def set_value(self, new_val):
        old_val = self._value
        self._value = new_val
        if self._before_first_set or old_val != new_val:
            self._before_first_set = False
            self._on_value_change()


class LightProperties:
    def __init__(self, name="unnamed lights", color=rgb(255, 255, 255), mode=DEFAULT_MODE, param=DEFAULT_PARAM):
        self.name = name
        self.on = Property(name + " on", 0)
        self.color = Property(name + " color", color)
        self.mode = Property(name + " mode", mode)
        self.param = Property(name + " param", param)

    def __repr__(self):
        mode = self.mode.value()
        param = self.param.value()
        r = f'LightProperties("{self.name}", {repr_as_hsv(self.color.value())}'
        if mode != DEFAULT_MODE:
            r += f", mode = {mode}"
        if param != DEFAULT_PARAM:
            r += f", param = {param}"
        r += ")"
        return r

    def copy(self):
        return LightProperties(self.name,
            color=self.color.value(),
            mode=self.mode.value(),
            param=self.param.value())


def repr_as_hsv(v):
    r, g, b = v
    h, s, v = rgb_to_hsv(r, g, b)
    return f"hsv({round(h, 3)}, {round(s, 3)}, {round(v, 3)})"



DEFAULT_ECOTRON_PROPERTIES = EcotronProperties()
