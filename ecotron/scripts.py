from director import Script, ScriptQueue
from tick_aware import TickAware
import ecotron.bebop.scripts as bebop_scripts
import ecotron.hyperscanner

class Scripter:
    def __init__(self, director, base, controls, master_controller):
        self.production_line = ProductionLineScripter(director, base, controls, master_controller)

class ProductionLineScripter(TickAware):

    # phases:
    # 1. hyperanalyzer
    # 2. move conveyor 5 links
    # 3. bot analysis
    # 4. move conveyor 5 links

    P0_DURATION = 8
    P1_LINKS = 5
    P2_DURATION = 10
    P3_LINKS = 5

    PLANT_DISTANCE_IN_LINKS = 10


    def __init__(self, director, base, controls, master_controller):
        TickAware.__init__(self)
        self._director = director
        
        self._conveyor = base.conveyor
        self._bebop = base.bebop
        self._hyperscanner = base.hyperscanner

        self._master_controller = master_controller

        self._conveyor_controls = controls.conveyor_controls

        self._production_line_on = False
        self._production_line_step_enqueued = False

        self._phase = 0
        self._last_phase_start = None
        self._phase_times = [ProductionLineScripter.P0_DURATION, 0, ProductionLineScripter.P2_DURATION, 0]

    @property
    def phase(self):
        return self._phase

    @phase.setter
    def phase(self, val):
        if val == self._phase:
            return
        if self._last_phase_start != None:
            self._phase_times[self._phase] = self.current_time() - self._last_phase_start
        self._phase = val
        self._last_phase_start = self.current_time()

    def conveyor_speed(self):
        pot = self._conveyor_controls.potentiometer.value
        if pot < 0.1:
            return 0
        else:
            return pot

    def _zero_safe_speed(self):
        return max(self.conveyor_speed(), 0.1)

    def tick(self, time_s, duration_s):
        if self._production_line_on and self.conveyor_speed() and not self._master_controller.calibration and not self._production_line_step_enqueued:
            self._enqueue_production_line_step()
        self._bebop.when_plants_moved(self._plant_positions())
        
    def _plant_positions(self):
        phase = self._conveyor.phase() / 2
        if self.phase >= 2:
            phase += 0.5
        plant_positions = [(i + phase) * ProductionLineScripter.PLANT_DISTANCE_IN_LINKS for i in [0, 1, 2, 3]]
        return plant_positions

    def _enqueue_production_line_step(self):
        self._production_line_step_enqueued = True
        self._enter_phase_0()

    def _enter_phase_0(self):
        self.phase = 0

        scanner_script = ecotron.hyperscanner.scan_cycle_script(self._hyperscanner, ProductionLineScripter.P0_DURATION)        
        self._director.execute(scanner_script)
        self._director.execute(Script()
            .add_sleep(ProductionLineScripter.P0_DURATION)
            .add_step(self._enter_phase_1)
        )

    def _enter_phase_1(self):
        self.phase = 1
        self._conveyor.move_links(ProductionLineScripter.P1_LINKS, self._zero_safe_speed(), self._enter_phase_2)

    def _enter_phase_2(self):
        self.phase = 2
        analyze_script = bebop_scripts.analyze_plant(self._bebop, ProductionLineScripter.P2_DURATION)
        
        expected_duration_till_next_analyze = sum(self._phase_times) - analyze_script.duration_s
        
        bebop_script = analyze_script.add(bebop_scripts.idle(self._bebop, expected_duration_till_next_analyze - 0.2))
        
        self._director.execute(bebop_script)
        self._director.execute(Script()
            .add_sleep(ProductionLineScripter.P2_DURATION)
            .add_step(self._enter_phase_3)
        )

    def _enter_phase_3(self):
        self.phase = 3
        self._conveyor.move_links(ProductionLineScripter.P3_LINKS, self._zero_safe_speed(), self._when_production_line_step_finished)

    def _when_production_line_step_finished(self):
        self._production_line_step_enqueued = False


    def production_line_on(self):
        self._production_line_on = True

    def production_line_off(self):
        self._production_line_on = False


    