import os
import pandas as pd
import json

files = [
    "black.csv",
    "white.csv",
    "red.csv",
    "green.csv",
    "blue.csv",
    "yellow.csv",
    "orange.csv"
]

# Dictionary to hold color means
color_means = {}

# List all CSV files in the directory
for filename in files:
    with open("color sampling/" + filename, 'r') as file:
        means = [0.0, 0.0, 0.0]
        lineNb = 0
        for line in file:
            lineNb += 1
            rgb = line.strip().strip('()').split(',')

            for i in range(3):
                means[i] += float(rgb[i])
    
        for i in range(3):
            means[i] /= lineNb

    # Assign the mean tuple to a color in the dictionary
    color_name = filename.split('.')[0]  # Get color name from filename
    color_means[color_name] = means

# Print the resulting dictionary
items = list(color_means.items())
for idx, (name, means) in enumerate(items):
    comma = ',' if idx < len(items) - 1 else ''
    vals = ','.join(str(int(m)) if float(m).is_integer() else str(m) for m in means)
    print(f'"{name}": [{vals}]{comma}')