import matplotlib.pyplot as plt
import csv

csv_file = "pid_log.csv"

timestamps, measured, error, P_term, I_term, D_term, output = [], [], [], [], [], [], []

with open(csv_file, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        timestamps.append(float(row["timestamp"]))
        measured.append(float(row["measured"]))
        error.append(float(row["error"]))
        P_term.append(float(row["P"]))
        I_term.append(float(row["I"]))
        D_term.append(float(row["D"]))
        output.append(float(row["output"]))

# convert timestamps to relative time
t0 = timestamps[0] if timestamps else 0
times = [t - t0 for t in timestamps]

plt.figure(figsize=(12, 6))
plt.plot(times, measured, label="Measured")
plt.plot(times, [measured[0]]*len(times), "--", label="Setpoint")  # Optional: replace with real setpoint
plt.plot(times, output, label="PID Output")
plt.plot(times, P_term, "--", label="P term")
plt.plot(times, I_term, "--", label="I term")
plt.plot(times, D_term, "--", label="D term")
plt.xlabel("Time (s)")
plt.ylabel("Value")
plt.title("PID Controller Log")
plt.legend()
plt.grid(True)
plt.show()
