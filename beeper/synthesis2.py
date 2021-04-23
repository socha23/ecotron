import pygame
import time
import numpy as np
import scipy.signal

import math

from sound import Clip

pygame.init()

mixer_settings = pygame.mixer.get_init()

SAMPLE_RATE = mixer_settings[0]
BITRATE = -mixer_settings[1]
SAMPLE_MAX_VAL = 2**(BITRATE - 1) - 1

def make_clip(*waveforms):
  return Clip(pygame.sndarray.make_sound(make_sample(*waveforms)))

def make_sample(*waveforms):
  waveform = np.concatenate(tuple(waveforms))
  scaled_array = np.int16(waveform * SAMPLE_MAX_VAL)
  stereo = np.tile(scaled_array[:, None], 2)
  return stereo

def _x(freq_hz, duration_s):
  return np.linspace(0, 2 * np.pi * freq_hz * duration_s, int(duration_s * SAMPLE_RATE))

def sine(freq_hz, duration_s=1):  
  return np.sin(_x(freq_hz, duration_s))

def sawtooth(freq_hz, duration_s=1):
  return scipy.signal.sawtooth(_x(freq_hz, duration_s))

def triangle(freq_hz, duration_s=1):
  return scipy.signal.sawtooth(_x(freq_hz, duration_s), 0.5)

def square(freq_hz, duration_s=1):
  return scipy.signal.square(_x(freq_hz, duration_s))

def cut(waveform, min_value=-1, max_value=1):
  return np.minimum(max_value, np.maximum(min_value, waveform))

def adsr(duration_s, attack=0.1, decay=0.1, sustain=0.2, release=0.1, attack_att = 1, decay_att = 0.7):
  a_t = int(duration_s * attack)
  d_t = int(duration_s * decay)
  s_t = int(duration_s * sustain)
  r_t = int(duration_s * SAMPLE_RATE) - a_t - d_t - s_t
  a = np.linspace(0, attack_att, a_t)
  d = np.linspace(attack_att, decay_att, d_t)
  s = np.linspace(decay_att, decay_att, s_t)
  r = np.linspace(decay_att, 0, r_t)
  return np.concatenate((a, d, s, r))
