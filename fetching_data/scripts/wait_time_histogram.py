import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the CSV file
df = pd.read_csv('fetch_timeline.csv')

# Create the histogram
plt.figure(figsize=(12, 7))
n, bins, patches = plt.hist(df['wait_time'], bins=10, color='skyblue', 
                           edgecolor='black', alpha=0.7)

# Add a vertical line for the mean wait time
mean_wait = df['wait_time'].mean()
plt.axvline(mean_wait, color='red', linestyle='dashed', linewidth=2)
plt.text(mean_wait + 2, plt.ylim()[1]*0.9, f'Mean: {mean_wait:.1f}s', 
         color='red', fontweight='bold')

# Add a vertical line for the median wait time
median_wait = df['wait_time'].median()
plt.axvline(median_wait, color='green', linestyle='dashed', linewidth=2)
plt.text(median_wait - 15, plt.ylim()[1]*0.8, f'Median: {median_wait:.1f}s', 
         color='green', fontweight='bold')

# Add labels and title
plt.xlabel('Wait Time (seconds)')
plt.ylabel('Frequency')
plt.title('Distribution of Wait Times Between Tweet Batches')
plt.grid(True, linestyle='--', alpha=0.7, axis='y')

# Add stats as text box
stats_text = (f'Min wait: {df["wait_time"].min()} seconds\n'
              f'Max wait: {df["wait_time"].max()} seconds\n'
              f'Total waits: {len(df)} batches\n'
              f'Total wait time: {df["wait_time"].sum()} seconds')

plt.figtext(0.75, 0.75, stats_text, 
            bbox={"facecolor":"lightyellow", "alpha":0.9, "pad":5})

# Save and show the plot
plt.tight_layout()
plt.savefig('wait_time_histogram.png', dpi=300, bbox_inches='tight')
plt.show()

print(f"Histogram saved as 'wait_time_histogram.png'")