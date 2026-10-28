from matplotlib import pyplot as plt
import math

# First dataset
FILE = "drive_bad5_line.csv"
DELAY_SEC = 0.1

with open(FILE, "r") as f:
    values = [float(x) for x in f.readlines()]

times = [DELAY_SEC * i for i in range(len(values))]

# Plot first dataset
plt.plot(times, values, label='In-line starting position')

# Add a second dataset (example with a different file)
FILE2 = "drive_bad5_angle.csv"
with open(FILE2, "r") as f:
    values2 = [float(x) for x in f.readlines()]

# Plot second dataset
plt.plot(times, values2, label='Offset starting position')

plt.xlabel("Time (s)")
plt.ylabel("Distance delta (cm)")
plt.yticks([x/2 for x in range(math.floor(min(min(values), min(values2)))*2, round(max(max(values), max(values2)))*2 + 1) if x % 1 == 0])
plt.legend()  # Add legend to distinguish between plots
plt.show()
