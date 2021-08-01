from ecotron.widget import Widget
from tick_aware import TimeAware
import random
import value_source

class _SleeperValueSource(value_source._Decorator):
    def __init__(self, source=value_source.AlwaysOn(), sleep_from=5, sleep_to=30, wake_from=7, wake_to=15, intensity=0.5):
        value_source._Decorator.__init__(self, value_source.FadeInOut(0.5, source))
        self._sleep_from = sleep_from
        self._sleep_to = sleep_to
        self._wake_from = wake_from
        self._wake_to = wake_to
        self._intensity = intensity

        self._wake_at = 0
        self._sleep_at = 0

        self._on = False
        self._sleeping = False

        self.turn_off()

    def go_to_sleep(self):
        self._wake_at = self.current_time() + random.uniform(self._sleep_from, self._sleep_to)
        self._inner_source.fade_out()
        self._sleeping = True

    def wake(self):
        self._sleep_at = self.current_time() + random.uniform(self._wake_from, self._wake_to)
        self._inner_source.fade_in()
        self._sleeping = False

    def turn_on(self):
        self._on = True
        self.go_to_sleep()

    def turn_off(self):
        self._on = False
        self.go_to_sleep()
    
    def value(self):
        if self._on:
            if self._sleeping and self._wake_at < self.current_time():
                self.wake()
            elif not self._sleeping and self._sleep_at < self.current_time():
                self.go_to_sleep()
        return value_source.multiply(self._inner_source.value(), self._intensity)


class Frog:
    def __init__(self, eye_light, sleep_from=5, sleep_to=30, wake_from=3, wake_to=20):
        self._eye_light = eye_light
        self._eye_light.source = _SleeperValueSource(value_source.EyeBlink(), sleep_from, sleep_to, wake_from, wake_to, 0.3)

    def turn_off(self):
        self._eye_light.source.turn_off()

    def turn_on(self):
        self._eye_light.source.turn_on()

    def wake(self):
        self._eye_light.source.wake()


class Jungle(Widget):

    def __init__(self, eye_lights=[]):
        Widget.__init__(self)
        self._frogs = []
        for light in eye_lights:
            self._frogs.append(Frog(light))
            
    def when_turn_on(self):
        for frog in self._frogs:
            frog.turn_on()
        random.choice(self._frogs).wake()

    def when_turn_off(self):
        for frog in self._frogs:
            frog.turn_off()
