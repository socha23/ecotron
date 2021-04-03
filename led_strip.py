import board
import neopixel

from threading import Thread
from time import sleep, time
from gpiozero import Button, PWMLED



NUM_PIXELS = 15

pixels = neopixel.NeoPixel(board.D21, NUM_PIXELS, auto_write=False)

strip_is_on = False

def execfile(s):
    exec(open(s).read())

def strip_off():
    pixels.fill((0, 0, 0))
    pixels.show()

def strip_on(color = (0, 128, 0)):
    pixels.fill(color)
    pixels.show()

def divide_color(color, divider):
    r, g, b = color
    return (int(r / divider), int(g / divider), int(b / divider)) 

def left_to_right(color = (0, 255, 0), bg_color = (0, 16, 0), speed_s = 1.0, pulse_width = 5):
    for i in range(-pulse_width, NUM_PIXELS+pulse_width):
        for px in range(NUM_PIXELS):
            if px == i:
                pixels[px] = color
            elif abs(px - i) <= pulse_width / 4:
                pixels[px] = divide_color(color, 2)
            elif abs(px - i) <= pulse_width / 2:
                pixels[px] = divide_color(color, 4)
            else:
                pixels[px] = bg_color
        pixels.show()        
        sleep(speed_s / (NUM_PIXELS+pulse_width))

def run_strip(color = (0, 64, 32), bg_color = (0, 0, 0), speed_pulse = 0.5, speed_pause = 1.0, pulse_width=5):
    while strip_is_on:
        left_to_right(color, bg_color, speed_pulse, pulse_width)
        strip_on(bg_color)
        sleep(speed_pause)

strip_off()

