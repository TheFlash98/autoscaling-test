import time
import csv
import os

class PIDController:
    def __init__(self, Kp, Ki, Kd, setpoint, csv_file="pid_log.csv"):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint

        self.integral = 0
        self.last_error = 0
        self.last_time = None

        self.csv_file = csv_file
        # Create CSV and write header if it doesn't exist
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, mode="w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "measured", "error", "P", "I", "D", "output"])

    def compute(self, measured_value):
        current_time = time.time()
        error = measured_value - self.setpoint

        if self.last_time is None:
            self.last_time = current_time
            self.last_error = error
            return 0  # no control on first run

        dt = current_time - self.last_time
        if dt <= 0:
            return 0

        # PID calculations
        self.integral += error * dt
        derivative = (error - self.last_error) / dt
        P = self.Kp * error
        I = self.Ki * self.integral
        D = self.Kd * derivative
        output = P + I + D

        # store values for next iteration
        self.last_error = error
        self.last_time = current_time

        # Print debug
        print(f"PID Debug -> P: {P:.4f}, I: {I:.4f}, D: {D:.4f}")

        # Append to CSV
        with open(self.csv_file, mode="a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([current_time, measured_value, error, P, I, D, output])

        return output
