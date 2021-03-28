from tick_aware import TickAware

class ValueSource(TickAware):
    def __init__(self):
        TickAware.__init__(self)

    def get_value(self):
        return 1

    def tick(self, cur_s, delta_s):
        pass

    def close(self):
        TickAware.close(self)


class ConstantSource(ValueSource):
    def __init__(self, val):
        ValueSource.__init__(self)
        self._val = val

    def value(self):
        return self._val


class AlwaysOnSource(ConstantSource):
    def __init__(self):
        ConstantSource.__init__(self, 1)


class AlwaysOffSource(ConstantSource):
    def __init__(self):
        ConstantSource.__init__(self, 0)


class SourceWatcher(TickAware):
    def __init__(self, on_change=lambda x: None):
        self._current_source = AlwaysOffSource()
        TickAware.__init__(self)
        self._last_val = None
        self._on_change = on_change

    def tick(self, cur_s, delta_s):
        new_val = self._current_source.value()
        if self._last_val != new_val:
            self._last_val = new_val
            if self._on_change != None:
                self._on_change(new_val)

    @property
    def source(self):
        return self._current_source

    @source.setter
    def source(self, new_source):
        if self._current_source != None:
            self._current_source.close()
        self._current_source = new_source

    def close(self):
        if self._current_source != None:
            self._current_source.close()


class SourceWatcherMixin:
    def __init__(self):
        self._source_watcher = SourceWatcher(self.on_value_change)

    def on_value_change(self, value):
        raise "Not implemented"

    @property 
    def source(self):
        return self._source_watcher.source

    @source.setter
    def source(self, new_source):
        self._source_watcher.source = new_source


class Blink(ValueSource):
    def __init__(self, time_on = 1, time_off = 1):
        ValueSource.__init__(self)
        self._time_on = time_on
        self._time_off = time_off
        self._cycle_start = self.current_time()

    def value(self):
        cur_time = self.current_time()
        delta = cur_time - self._cycle_start
        if delta < self._time_on:
            return 1
        elif delta < self._time_on + self._time_off:
            return 0
        else:
            cycle_time = self._time_on + self._time_off
            self._cycle_start = self._cycle_start + (int(delta / cycle_time) * cycle_time)
            return self.value


     