def translate(val, from_a, from_b, to_a, to_b):
  return ((val - from_a) / (from_b - from_a)) * (to_b - to_a) + to_a