from director import Director, Script, script_with_sleep
from ecotron.widget import Widget
from tick_aware import TimeAware
import random
import value_source

ANGLE_WELDING_MIN = 120
ANGLE_WELDING_MAX = 180
ANGLE_HEAD_MIN = 100
ANGLE_HEAD_MAX = 120
ANGLE_OUTSIDE_MIN = 0
ANGLE_OUTSIDE_MAX = 100

class RepairTable(Widget, TimeAware):

    def __init__(self, director, robot_light, welder_light, welder_servo):
        Widget.__init__(self)
        TimeAware.__init__(self)
        self._director = director
        self._robot_light = robot_light
        self._welder_light = welder_light
        self._welder_servo = welder_servo
        
        self._last_action_completed_at = 0
        self._current_script_executor = None

    def when_turn_on(self):
        self._robot_light.source = value_source.EyeBlink()
        self._do_random_action()

    def when_turn_off(self):
        self._robot_light.source = value_source.AlwaysOff()
        if self._current_script_executor:
            self._current_script_executor.cancel()
            self._current_script_executor = None

    def _execute(self, script):
        self._current_script_executor = self._director.execute(script)


    def _do_random_action(self):
        action = random.randint(0, 10)
        if action < 5:
            self._do_some_welding()
        elif action < 8:
            self._look_at_head()
        else:
            self._look_at_outside()


    def _pause(self):
        MIN_IDLE_TIME = 3
        MAX_IDLE_TIME = 10

        self._execute(Script()
            .add_sleep(random.uniform(MIN_IDLE_TIME, MAX_IDLE_TIME))
            .add_step(lambda: self._pause_completed())
        )

    def _action_completed(self):
        self._pause()

    def _pause_completed(self):
        self._do_random_action()

    def _do_some_welding(self):
        script = Script()

        script.add_step(lambda: self._welder_servo.set_angle(random.randint(ANGLE_WELDING_MIN, ANGLE_WELDING_MAX)))
        script.add_sleep(1)

        for _ in range(random.randint(3, 7)):
            script.add_step(lambda: self._welder_servo.set_angle(random.randint(ANGLE_WELDING_MIN, ANGLE_WELDING_MAX)))
            script.add_sleep(0.6)
            
            ONE_BLINK_DURATION = 0.1

            repetitions = random.randint(2, 20)
            time = repetitions * ONE_BLINK_DURATION

            script.add_step(lambda: self._welder_light.set_source(value_source.repeated_blink(how_many = repetitions, duration = ONE_BLINK_DURATION)))
            script.add_sleep(time + 0.5)
            
        script.add_step(lambda: self._action_completed())
        self._execute(script)

    def _look_at_head(self):
        self._execute(Script()
            .add_step(lambda: self._welder_servo.set_angle(random.randrange(ANGLE_HEAD_MIN, ANGLE_HEAD_MAX)))
            .add_sleep(0.6)
            .add_step(lambda: self._action_completed())
        )

    def _look_at_outside(self):
        self._execute(Script()
            .add_step(lambda: self._welder_servo.set_angle(random.randint(ANGLE_OUTSIDE_MIN, ANGLE_OUTSIDE_MAX)))
            .add_sleep(1)
            .add_step(lambda: self._action_completed())
        )
    