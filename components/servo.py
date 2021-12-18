import atexit
from tick_aware import TickAware, TimeAware

class ServoAnimator(TimeAware):

    FPS = 60

    def __init__(self, servo):
        TimeAware.__init__(self)
        self._servo = servo

        self._move_start_time = None
        self._move_start_angle = None

        self._move_end_time = None
        self._move_end_angle = None

        self._last_frame_at = 0

        self._callback = None

    def animate_move(self, angle_from, angle_to, duration_s, callback = None):
        if angle_from == angle_to:
            if callback != None:
                callback()
            return

        self._callback = callback
        self._move_start_angle = angle_from
        self._move_start_time = self.current_time()

        self._move_end_angle = angle_to
        self._move_end_time = self.current_time() + duration_s

    def is_animating(self):
        return self._move_start_time != None

    def stop(self):
        if self._callback:
            self._callback()

        self._move_start_time = None
        self._move_start_angle = None
        self._move_end_time = None
        self._move_end_angle = None

    def tick(self):
        if not self.is_animating():
            return

        time = self.current_time()

        if time - self._last_frame_at < 1 / ServoAnimator.FPS:
            return

        self._last_frame_at = time

        d_t = (time - self._move_start_time) / (self._move_end_time - self._move_start_time)

        d_t = max(0, min(1, d_t))
        new_angle = self._move_start_angle + (self._move_end_angle - self._move_start_angle) * d_t
        self._servo.angle = new_angle

        if d_t == 1:
            self.stop()


class Servo(TickAware):

    MIN_DISTANCE = 1
    SERVO_TOLERANCE = 0.5

    def __init__(self, servo_from_servokit, angle=90, min_angle=0, max_angle=180, min_pulse_witdh_range=750, max_pulse_witdh_range=2250):
        TickAware.__init__(self)
        self._servo = servo_from_servokit
        self._servo.set_pulse_width_range(min_pulse_witdh_range, max_pulse_witdh_range)
        atexit.register(self.close)

        self._angle = angle
        self.min_angle = min_angle
        self.max_angle = max_angle
        self._move_started_on = self.current_time()

        self._servo.angle = angle

        self._animator = ServoAnimator(self)

    def tick(self, time, delta_s):

        self._animator.tick()

        # hush
        HUSH_AFTER = 0.5

        ALWAYS_HUSH_AFTER = 5

        if (self._move_started_on != None
                and (
                    (time - self._move_started_on > HUSH_AFTER and abs(self._angle - self._servo.angle) < Servo.SERVO_TOLERANCE)
                    or time - self._move_started_on > ALWAYS_HUSH_AFTER
                )):
            self._servo.angle = None
            self._move_started_on = None

    def close(self):
        self._servo.angle = None

    def move_to(self, new_angle, speed=1, callback=None):
        speed = max(speed, 0.1)
        angle_per_s = 360 * speed # speed * (self.max_angle - self.min_angle)
        duration = abs(new_angle - self._angle) / angle_per_s
        self._animator.animate_move(self._angle, new_angle, duration, callback)

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


