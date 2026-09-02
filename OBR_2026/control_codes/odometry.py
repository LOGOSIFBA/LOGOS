import math

class Odometry:
    def __init__ (self):
        self.x = 0
        self.y = 0
        self.theta = 0
        self.wheel_radius = 0.0229
        self.wheel_base = 0.123
        self.last_right_deg = None
        self.last_left_deg = None
    
    def update (self, right_deg, left_deg):
        if self.last_right_deg is None or self.last_left_deg is None:
            self.last_right_deg = right_deg
            self.last_left_deg = left_deg
            return
        
        delta_right_deg = right_deg - self.last_right_deg
        delta_left_deg = left_deg - self.last_left_deg

        delta_right_turns = delta_right_deg / 360
        delta_left_turns = delta_left_deg / 360

        d_right = delta_right_turns * 2 * math.pi * self.wheel_radius
        d_left = delta_left_turns * 2 * math.pi * self.wheel_radius

        d_avg = (d_right + d_left)/2
        delta_theta = (d_right - d_left) / self.wheel_base
        theta_mid = self.theta + delta_theta/2

        delta_x = d_avg * math.cos(theta_mid)
        delta_y = d_avg * math.sin(theta_mid)

        self.x += delta_x
        self.y += delta_y
        self.last_left_deg = left_deg
        self.last_right_deg = right_deg
        self.theta += delta_theta
        self.theta = math.atan2(math.sin(self.theta), math.cos(self.theta))

    def get_position (self):
        return {
            "x": self.x,
            "y": self.y,
            "theta_rad": self.theta,
            "theta_deg": math.degrees(self.theta),
        }

    def reset (self):
        self.x = 0
        self.y = 0
        self.theta = 0
        self.last_right_deg = None
        self.last_left_deg = None

    def angle_difference_rad(self, current_angle, start_angle):
        difference = current_angle - start_angle

        while difference > math.pi:
            difference -= 2 * math.pi

        while difference < -math.pi:
            difference += 2 * math.pi

        return difference
