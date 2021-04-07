import pygame
import time
import numpy
import math

from sound import Clip

pygame.init()

mixer_settings = pygame.mixer.get_init()

SAMPLE_RATE = mixer_settings[0]
BITRATE = -mixer_settings[1]
SAMPLE_MAX_VAL = 2**(BITRATE - 1) - 1

def make_sample(duration_s, generator):
  sample_count = int(round(duration_s * SAMPLE_RATE))
  samples = numpy.zeros((sample_count, 2), dtype=numpy.int16)

  for sample_idx in range(sample_count):
    time_s = float(sample_idx) / SAMPLE_RATE
    val = int(SAMPLE_MAX_VAL * generator[time_s])
    samples[sample_idx] = [val, val]
  return samples

def make_clip(*samples):
  return Clip(pygame.sndarray.make_sound(numpy.concatenate(tuple(samples))))


class Sine:
  def __init__(self, freq_hz):
    self.freq_hz = freq_hz

  def __getitem__(self, time_s):
    return math.sin(2 * math.pi * self.freq_hz * time_s)


class Sawtooth:
  def __init__(self, freq_hz):
    self.freq_hz = freq_hz

  def __getitem__(self, time_s):
    phase = (time_s * self.freq_hz) % 1
    return transpond(phase, 0, 1, -1, 1)


class Triangle:
  def __init__(self, freq_hz):
    self.freq_hz = freq_hz

  def __getitem__(self, time_s):
    phase = (time_s * self.freq_hz) % 1
    if phase <= 0.5:
      return transpond(phase, 0, 0.5, -1, 1)
    else:
      return transpond(phase, 0.5, 1, 1, -1)


class Square:
  def __init__(self, freq_hz):
    self.freq_hz = freq_hz

  def __getitem__(self, time_s):
    phase = (time_s * self.freq_hz) % 1
    if phase <= 0.5:
      return -1
    else:
      return 1


class Const:
  def __init__(self, val):
    self.val = val

  def __getitem__(self, time_s):
    return self.val


class Multiply:
  def __init__(self, *functors):
    self.functors = functors

  def __getitem__(self, time_s):
    val = 1
    for f in self.functors:
      if isinstance(f, int) or isinstance(f, float):
        val *= f
      else:
        val *= f[time_s]
    return val


class Add:
  def __init__(self, *functors):
    self.functors = functors

  def __getitem__(self, time_s):
    val = 1
    for f in self.functors:
      val += f[time_s]
    return val


class Cut:
  def __init__(self, inner_generator, min_value=-1, max_value=1):
    self.inner_generator = inner_generator
    self.min_value = min_value
    self.max_value = max_value

  def __getitem__(self, time_s):
    return min(self.max_value, max(self.min_value, self.inner_generator[time_s]))


class ADSR:
  def __init__(self, attack=0.1, decay=0.1, sustain=0.2, release=0.1, attack_att = 1, decay_att = 0.7):
    self.attack = attack
    self.decay = decay
    self.sustain = sustain
    self.release = release
    self.attack_att = attack_att
    self.decay_att = decay_att

  def __getitem__(self, time_s):
    a = self.attack
    ad = a + self.decay
    ads = ad + self.sustain
    adsr = ads + self.release

    if time_s < a:
      return transpond(time_s, 0, a, 0, self.attack_att)
    elif time_s < ad:
      return transpond(time_s, a, ad, self.attack_att, self.decay_att)
    elif time_s < ads:  
      return self.decay_att
    elif time_s < adsr:    
      return transpond(time_s, ads, adsr, self.decay_att, 0)
    else: 
      return 0


def transpond(val, from_a, from_b, to_a, to_b):
  return ((val - from_a) / (from_b - from_a)) * (to_b - to_a) + to_a