import random
from director import execute, Script

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

    def bind_to_property(self, property):
        property.on_value_change = lambda x: self.turn_on() if x == 1 else self.turn_off()


class MultiWidget(Widget):
    def __init__(self, *widgets):
        Widget.__init__(self)
        self._widgets = widgets
        self._on = False

    def when_turn_on(self):
        for w in self._widgets:
            w.on = True

    def when_turn_off(self):
        for w in self._widgets:
            w.on = False


class Actor(Widget):
    def __init__(self):
        Widget.__init__(self)
        self._current_script_executor = None

    def when_turn_off(self):
        if self._current_script_executor:
            self._current_script_executor.cancel()
            self._current_script_executor = None

    def _execute(self, script):
        self._current_script_executor = execute(script)


class PausingActor(Actor):
    def __init__(self, min_idle_time=1, max_idle_time=5):
        Actor.__init__(self)
        self._min_idle_time = min_idle_time
        self._max_idle_time = max_idle_time

    def when_turn_on(self):
        self._do_action()

    def _do_action(self):
        self._execute(Script()
            .add_async_step(lambda c: self.do_action(c))
            .add_step(self._action_completed)
        )

    def _pause(self):
        self._execute(Script()
            .add_sleep(random.uniform(self._min_idle_time, self._max_idle_time))
            .add_step(self._pause_completed)
        )

    def _action_completed(self):
        self._pause()

    def _pause_completed(self):
        self._do_action()

    def force_action(self, action):
        self._execute(Script()
            .add_async_step(lambda c: action(c))
            .add_step(self._action_completed)
        )

    # OVERRIDE THIS
    def do_action(self, callback):
        callback()







