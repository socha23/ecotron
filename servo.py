from gpiozero import Servo
from time import sleep

#hd1370a = Servo(13, 0.0015, 0.001, 0.002)
#hd1370a = Servo(13, 0.0015, 0.0008, 0.0022)
hd1370a = Servo(13, 0.0015, 0.0003, 0.003)

hd1370a.max()
input()


#while True:
#    hd1370a.min()
#    sleep(1)
#    hd1370a.mid()
#    sleep(1)
#    hd1370a.max()
#    sleep(1)
