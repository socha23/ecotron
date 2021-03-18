from gpiozero import PWMLED

from time import sleep

leds = [PWMLED(21), PWMLED(20), PWMLED(16)]

for led in leds:
    led.pulse()

sleep(10)
