from value_source import ValueSource

def rgb(r, g, b):
    return (r / 256, g / 256, b / 256)


class EcotronProperties:
    def __init__(self):
        self.master_volume = Property("Master volume", 1)
        self.light_strip_on = Property("Light strip on", 1)
        self.fans_on = Property("Fans on", 0)
        self.repair_table_on = Property("Repair table on", 0)
        self.elevator_lights_on = Property("Elevator lights on", 1)
        self.door_lights_on = Property("Door lights on", 1)
        self.top_lights_floor_1_on = Property("Top lights floor 1 on", 1)
        self.jungle_on = Property("Jungle on", 0)

        self.door_lights_color = Property("Door lights color RGB", rgb(20, 30, 60))
        self.floor_lights_color = Property("Floor lights color RGB", rgb(10, 60, 50))
        self.top_lights_floor_1_color = Property("Top lights floor 1 color RGB", rgb(60, 50, 20))


class Property:
    def __init__(self, name="unnamed property", initial_value=None):
        self._value = initial_value
        self._before_first_set = True
        self.on_value_change = lambda x: None
        self._name = name

    def _on_value_change(self):
        self.on_value_change(self.value())

    def value(self):
        return self._value

    def set_value(self, new_val):
        old_val = self._value
        self._value = new_val
        if self._before_first_set or old_val != new_val:
            self._before_first_set = False
            self._on_value_change()
