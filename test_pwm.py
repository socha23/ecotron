from adafruit_servokit import ServoKit
from time import sleep
from components.led import PWMLED
from tick_aware import DEFAULT_CONTROLLER, TickAware
from value_source import AlwaysOff, AlwaysOn, Sine, ValueSource, Multiply, Constant


kit = ServoKit(channels=16, address=0x43)

#leds = [PWMLED(kit._pca.channels[c]) for c in range(8)]
leds = [PWMLED(kit._pca.channels[c]) for c in [8, 9]]
DEFAULT_CONTROLLER.on = True

for led in leds:
    led.source = Sine()
print("sine")
input()
for led in leds:
    led.source = AlwaysOff()
input()

