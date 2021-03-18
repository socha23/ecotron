import pygame
import time

pygame.init()

class Clip:
  def __init__(self, path, volume=1, stereo=None):
    if stereo is None:
        stereo = [1, 1]
    self._stereo = stereo
    self._path = path
    self._volume = volume

  def play(self):
    self._sound = pygame.mixer.Sound(self._path)
    left, right = self._stereo
    self._channel = self._sound.play()
    self._channel.set_volume(left * self.get_volume(), right * self.get_volume())

  def get_volume(self):
    return self._volume

  def set_volume(self, volume):
    self._volume = volume
    self._sound.set_volume(volume)


def play_mp3(path):
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()


def play(path, volume=1, stereo=None):
    sound = Clip(path, volume, stereo)
    sound.play()
    return sound


def max_channels():
    return pygame.mixer.get_num_channels()


def wait_until_end():
    while pygame.mixer.get_busy():
      time.sleep(0.2)
