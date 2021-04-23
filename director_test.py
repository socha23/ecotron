import unittest

from director import Script, Director
from tick_aware import TickAwareController, TickAware

class TestDirector(unittest.TestCase):

    def setUp(self):
        self.tick_aware_controller = TickAwareController(initial_time=0)
        self.director = Director(tick_aware_controller = self.tick_aware_controller)


    def test_basic_sequence(self):
        results = []
        
        self.director.execute(Script()
            .add_step(lambda: results.append("a"))
            .add_step(lambda: results.append("b"))
            .add_step(lambda: results.append("c"))
            )
        self.tick_aware_controller.tick(1)

        self.assertEqual(results, ["a", "b", "c"])
        self.assertEqual(self.director.script_runner_count(), 0)
        

    def test_on_complete(self):
        results = []
        
        self.director.execute(Script()
            .add_step(lambda: results.append("a")
        ), on_complete = lambda: results.append("b"))
        self.tick_aware_controller.tick(1)

        self.assertEqual(results, ["a", "b"])


    def test_sleep(self):
        results = []
        
        self.director.execute(Script()
            .add_step(lambda: results.append("a"))
            .add_sleep(2)
            .add_step(lambda: results.append("b"))
        )

        self.assertEqual(results, [])
        self.assertEqual(self.director.script_runner_count(), 1)

        self.tick_aware_controller.tick(1)

        self.assertEqual(results, ["a"])
        self.assertEqual(self.director.script_runner_count(), 1)

        self.tick_aware_controller.tick(2)

        self.assertEqual(results, ["a", "b"])
        self.assertEqual(self.director.script_runner_count(), 0)

    def test_sleeps_side_by_side(self):
        results = []
        
        self.director.execute(Script()
            .add_step(lambda: results.append("a"))
            .add_sleep(1)
            .add_sleep(1)
            .add_step(lambda: results.append("b"))
        )

        self.tick_aware_controller.tick(1)
        self.assertEqual(results, ["a"])

        self.tick_aware_controller.tick(2)
        self.assertEqual(results, ["a", "b"])

    def test_sleeps_side_by_side_one_step(self):
        results = []
        
        self.director.execute(Script()
            .add_step(lambda: results.append("a"))
            .add_sleep(1)
            .add_sleep(1)
            .add_step(lambda: results.append("b"))
        )

        self.tick_aware_controller.tick(2)
        self.assertEqual(results, ["a", "b"])

    def test_async(self):
        results = []
        
        self.director.execute(Script()
            .add_async_step(lambda callback: _AsyncJob(self.tick_aware_controller, results, "a", 1, callback))
            .add_async_step(lambda callback: _AsyncJob(self.tick_aware_controller, results, "b", 1, callback))
        )

        self.tick_aware_controller.tick(1)
        self.assertEqual(results, ["a"])

        self.tick_aware_controller.tick(2)
        self.assertEqual(results, ["a", "b"])


    def test_mixed(self):
        results = []        
        self.director.execute(Script()
            .add_async_step(lambda callback: _AsyncJob(self.tick_aware_controller, results, "a", 1, callback))
            .add_sleep(1)
            .add_step(lambda: results.append("b"))
            .add_sleep(1)
            .add_async_step(lambda callback: _AsyncJob(self.tick_aware_controller, results, "c", 1, callback))
            .add_async_step(lambda callback: _AsyncJob(self.tick_aware_controller, results, "d", 1, callback))
            .add_step(lambda: results.append("e"))
            , on_complete=lambda: results.append("f")
        )

        for t in range(6):
            self.tick_aware_controller.tick(t)
        self.assertEqual(results, ["a", "b", "c", "d", "e", "f"])

    def test_coexecute(self):
        results = []        
        self.director.execute(Script()
            .add_parallel(
                Script().add_sleep(1).add_step(lambda: results.append("a")),
                Script().add_sleep(2).add_step(lambda: results.append("b")),
                Script().add_sleep(3).add_step(lambda: results.append("c"))
            )
            .add_step(lambda: results.append("d"))
        )

        for t in range(6):
            self.tick_aware_controller.tick(t)
        self.assertEqual(results, ["a", "b", "c", "d"])


class _AsyncJob(TickAware):
    def __init__(self, controller, results, value, duration_s, on_complete):
        TickAware.__init__(self, controller)
        self._results = results
        self._value = value
        self._duration_s = duration_s
        self._on_complete = on_complete
        self._time_start = controller.current_time()

    def tick(self, time_s, delta_s):
        if time_s >= self._time_start + self._duration_s:
            self._results.append(self._value)
            self.close()
            self._on_complete()

if __name__ == '__main__':
    unittest.main()