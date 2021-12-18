from tick_aware import TickAware

MEASURES_COUNT = 5

MIN_DELTA = 0.01

GRADIENT_DOWN = -1
GRADIENT_UP = 1


class DistanceMeter(TickAware):

  def __init__(self, analog_value_provider):
    TickAware.__init__(self)
    self._value_provider = analog_value_provider
    self._gradient = None
    self._measures = [0] * MEASURES_COUNT
    self.on_object_passed = lambda: None

  def tick(self, current_time, delta_t):
    val = self._value_provider()
    if abs(self._measures[-1] - val) > MIN_DELTA:
      self._measures.pop(0)
      self._measures.append(val)
      new_gradient = self._determine_gradient()
      if new_gradient != None:
        if self._gradient == None:
          self._gradient = new_gradient
        elif self._gradient != new_gradient:
          self._on_gradient_change(self._gradient, new_gradient)
          self._gradient = new_gradient

  def _on_gradient_change(self, gradient_from, gradient_to):
    if gradient_from == GRADIENT_DOWN and gradient_to == GRADIENT_UP:
      self.on_object_passed()

  def value(self):
    return self._analog_value_provider()

  def _determine_gradient(self):
    dir = 0
    for i in range(MEASURES_COUNT - 1):
      if self._measures[i] < self._measures[i + 1]:
        dir += 1
      elif self._measures[i] > self._measures[i + 1]:
        dir -= 1
    if dir == MEASURES_COUNT - 1:
      return GRADIENT_UP
    elif dir == -(MEASURES_COUNT - 1):
      return GRADIENT_DOWN
    else:
      return None
