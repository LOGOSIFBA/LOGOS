import time

class PID:
    def __init__ (self):
        self.kp = 100
        self.ki = 0
        self.kd = 0.1
        self.last_error = None
        self.integral = 0
        self.last_time = None
        self.set_point = 0

    def calculate(self, position):
        now = time.monotonic()
        error = self.set_point - position

        if self.last_time is None or self.last_error is None:
            derivative = 0
        else:
            dt = now - self.last_time
            if dt > 0.15 or dt <= 0:
                derivative = 0
            else:
                derivative = (error - self.last_error)/dt
                self.integral += error * dt

        result = self.kp * error + self.ki * self.integral + self.kd * derivative
        result = max(-100, min(100, result))
        self.last_time = now
        self.last_error = error
        return result
