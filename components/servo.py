import atexit
from tick_aware import TickAware
from time import sleep

class Servo(TickAware):

    MIN_DISTANCE = 3

    def __init__(self, servo_from_servokit, angle=90, min_angle=0, max_angle=180):        
        TickAware.__init__(self)
        self._servo = servo_from_servokit
        atexit.register(self.close)

        self._angle = angle
        self.min_angle = min_angle
        self.max_angle = max_angle
        self._move_started_on = self.current_time()
        self._servo.angle = angle

    def tick(self, time, delta_s):
        HUSH_AFTER = 0.5
        SERVO_TOLERANCE = 5
        if (self._move_started_on != None 
                and time - self._move_started_on > HUSH_AFTER 
                and abs(self._angle - self._servo.angle) < SERVO_TOLERANCE):
            self._servo.angle = None
            self._move_started_on = None

    def close(self):
        self._servo.angle = None        

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, new_angle):
        if new_angle != None:
            dest_angle = min(self.max_angle, max(self.min_angle, new_angle))
            if abs(self._angle - dest_angle) > Servo.MIN_DISTANCE:
                self._angle = dest_angle
                self._servo.angle = dest_angle
                self._move_started_on = self.current_time()
        else:
            self._angle = None
            self._servo.angle = None
       
    def set_angle(self, new_angle):
        self.angle = new_angle
    

