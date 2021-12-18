class XyController:
    def __init__(self):
        self._current_listener = None

    def change_x(self, sign):
        if self._current_listener:
            self._current_listener.on_x_changed(sign)

    def change_y(self, sign):
        if self._current_listener:
            self._current_listener.on_y_changed(sign)

    def set_current_listener(self, listener):
        self._current_listener = listener


class XyListener:
    def __init__(self):
        pass

    def on_x_changed(self, sign):
        pass

    def on_y_changed(self, sign):
        pass

DEFAULT_XY_CONTROLLER = XyController()

