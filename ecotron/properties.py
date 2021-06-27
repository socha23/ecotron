class EcotronProperties:
    def __init__(self):
        self.master_volume = Property("Master volume", 1)
        self.light_strip_on = Property("Light strip on", 1)
        self.fans_on = Property("Fans on", 0)


class Property:
    def __init__(self, name="unnamed property", initial_value=None):
        self._value = None
        self.on_value_change = lambda x: None
        self._name = name

    def _on_value_change(self):
        self.on_value_change(self.value())
        print(f"Setting [{self._name}] to {self.value()}")

    def value(self):
        return self._value

    def set_value(self, new_val):
        old_val = self._value
        self._value = new_val
        if old_val != new_val:
            self._on_value_change()

