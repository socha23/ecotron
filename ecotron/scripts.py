from director import Script, ScriptQueue
from tick_aware import TickAware

class ProductionLineScripter(TickAware):

    # phases:
    # 1. move conveyor 5 links
    # 2. hyperanalyzer
    # 3. move conveyor 5 links
    # 4. bot analysis


    def __init__(self, director, base):
        TickAware.__init__(self)
        self._script_queue = ScriptQueue(director)
        
        self._conveyor = base.conveyor
        self._bebop = base.bebop

        self.production_line_on = False
        self._production_line_step_enqueued = False


    def tick(self, time_s, duration_s):
        if self.production_line_on and not self._production_line_step_enqueued:
            self._enqueue_production_line_step()

    def _enqueue_production_line_step(self):
        self._production_line_step_enqueued = True
        self._enter_phase_1()

    def _enter_phase_1(self):
        self._conveyor.move_one_step(self._enter_phase_2)

    def _enter_phase_2(self):
        self._conveyor.move_one_step(self._enter_phase_2)


        self._script_queue.enqueue(Script()
            .add_async_step(lambda c : )
         )
        
        )





    