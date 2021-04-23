from tick_aware import TickAware, DEFAULT_CONTROLLER

class _SyncStep:
    def __init__(self, handler):
        self.handler = handler
        self.duration_s = 0

class _AsyncStep:
    def __init__(self, handler):
        self.handler = handler
        self.duration_s = 0

class _SleepStep:
    def __init__(self, duration_s):
        self.duration_s = duration_s

class _ParallelStep:
    def __init__(self, scripts):
        self.scripts = scripts
        self.duration_s = max([s.duration_s for s in scripts])

class Script:

    def __init__(self):
        self.steps = []

    @property
    def duration_s(self):
        return sum([step.duration_s for step in self.steps])

    def add_step_at_start(self, handler):
        self.steps.insert(0, _SyncStep(handler))
        return self

    def add_step(self, handler):
        self.steps.append(_SyncStep(handler))
        return self

    def add_async_step(self, handler):
        self.steps.append(_AsyncStep(handler))
        return self

    def add_sleep(self, duration_s):
        self.steps.append(_SleepStep(duration_s))
        return self

    def add_parallel(self, *scripts):
        self.steps.append(_ParallelStep(scripts))
        return self

    def add(self, script):
        self.steps.extend(script.steps)
        return self

    

def script_with_step(handler):
    return Script().add_step(handler)


class _ScriptRunner(TickAware):

    _STATE_RUNNING = 0
    _STATE_SLEEPING = 1
    _STATE_WAITING_FOR_ASYNC_RETURN = 2
    _STATE_AFTER_ASYNC_RETURN = 3
    _STATE_WAITING_FOR_SUBSCRIPTS_TO_FINISH = 4
    _STATE_COMPLETE = 5

    def __init__(self, script, director, on_complete):
        TickAware.__init__(self, director._tick_aware_controller)
        self._director = director
        self._script = script
        self._current_step = 0
        self._on_complete = on_complete
        self._state = _ScriptRunner._STATE_RUNNING
        self._sleep_left = 0
        self._subscript_runners = []

    def tick(self, cur_s, delta_s):
        self._proceed(delta_s)


    def _proceed(self, delta_s):
        current_step = self._script.steps[self._current_step]

        if isinstance(current_step, _SleepStep):
            if self._state == _ScriptRunner._STATE_RUNNING:
                self._sleep_left = current_step.duration_s
            if self._sleep_left <= delta_s:    
                time_left = delta_s - self._sleep_left
                self._state = _ScriptRunner._STATE_RUNNING
                self._sleep_left = 0
                self._current_step_finished(time_left)
            else:
                self._state = _ScriptRunner._STATE_SLEEPING
                self._sleep_left -= delta_s
        elif isinstance(current_step, _SyncStep):
            current_step.handler()
            self._current_step_finished(delta_s)
        elif isinstance(current_step, _ParallelStep):
            if self._state == _ScriptRunner._STATE_RUNNING:
                self._state = _ScriptRunner._STATE_WAITING_FOR_SUBSCRIPTS_TO_FINISH
                for s in current_step.scripts:
                    self._subscript_runners.append(self._director.execute(s))
            elif self._state == _ScriptRunner._STATE_WAITING_FOR_SUBSCRIPTS_TO_FINISH:
                proceed = True
                for runner in self._subscript_runners:
                    if not runner.is_complete():
                        proceed = False
                if proceed:
                    self._subscript_runners = []
                    self._state = _ScriptRunner._STATE_RUNNING
                    self._current_step_finished(delta_s)                    
        elif isinstance(current_step, _AsyncStep):
            if self._state == _ScriptRunner._STATE_RUNNING:
                self._state = _ScriptRunner._STATE_WAITING_FOR_ASYNC_RETURN
                current_step.handler(self._async_return)
            elif self._state == _ScriptRunner._STATE_AFTER_ASYNC_RETURN:
                self._state = _ScriptRunner._STATE_RUNNING
                self._current_step_finished(delta_s)

    def is_complete(self):
        return self._state == _ScriptRunner._STATE_COMPLETE


    def _async_return(self):
        self._state = _ScriptRunner._STATE_AFTER_ASYNC_RETURN

    def _current_step_finished(self, delta_s):
        self._current_step += 1
        if self._current_step == len(self._script.steps):
            self.close()
            self._director._unregister_runner(self)
            self._state = _ScriptRunner._STATE_COMPLETE
            self._on_complete()
        else: 
            self._proceed(delta_s)

class Director(TickAware):

    def __init__(self, tick_aware_controller = DEFAULT_CONTROLLER):
        TickAware.__init__(self, controller=tick_aware_controller)
        self._script_runners = set()


    def _unregister_runner(self, runner):
        self._script_runners.remove(runner)

    def tick_aware_controller(self):
        return self._tick_aware_controller
    
    def script_runner_count(self):
        return len(self._script_runners)

    def execute(self, script, on_complete=lambda:None):
        runner = _ScriptRunner(script, self, on_complete)
        self._script_runners.add(runner)
        return runner

class ScriptQueue:
    def __init__(self, director, on_complete=lambda:None):
        self._director = director
        self._current_script = None
        self._script_queue = []
        self._on_complete = on_complete

    def _execute_next_from_queue(self):
        if self._script_queue:
            self._current_script = self._script_queue.pop(0)
            self._director.execute(self._current_script, on_complete=self._when_current_script_execution_complete)
        else:
            if self._on_complete:
                self._on_complete()

    def _when_current_script_execution_complete(self):
        self._current_script = None
        self._execute_next_from_queue()

    def enqueue(self, script):
        self._script_queue.append(script)
        if not self._current_script:
            self._execute_next_from_queue()

    def replace_queue(self, script):
        self._script_queue = [script]
        if not self._current_script:
            self._execute_next_from_queue()
