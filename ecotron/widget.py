class Widget:
    def __init__(self, is_on = False):
        self._on = is_on

    def when_turn_on(self):
        pass

    def when_turn_off(self):
        pass    

    @property
    def on(self):
        return self._on

    @on.setter
    def on(self, val):
        if self._on == val:
            return
        self._on = val
        if val:
            self.when_turn_on()
        else:
            self.when_turn_off()

    def turn_on(self):
        self.on = True

    def turn_off(self):
        self.on = False