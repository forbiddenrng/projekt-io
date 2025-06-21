import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the CSV file
df = pd.read_csv('fetch_timeline.csv')

# Create the bar chart
plt.figure(figsize=(14, 7))
bars = plt.bar(df['seconds'], df['batch_tweet_count'], width=15, alpha=0.7)

# Add labels and title
plt.xlabel('Time (seconds)')
plt.ylabel('Tweets per Batch')
plt.title('Number of Tweets Fetched in Each Batch Over Time')
plt.grid(True, linestyle='--', alpha=0.5, axis='y')

# Add average line
avg_batch_size = df['batch_tweet_count'].mean()
plt.axhline(y=avg_batch_size, color='r', linestyle='--', alpha=0.7)
plt.text(df['seconds'].iloc[-1]/2, avg_batch_size + 1, 
         f'Average: {avg_batch_size:.1f} tweets per batch', 
         color='red')

# Calculate stats
total_tweets = df['batch_tweet_count'].sum()
max_batch = df['batch_tweet_count'].max()
min_batch = df['batch_tweet_count'].min()

# Add stats as text box
stats_text = (f'Total Tweets: {total_tweets}\n'
              f'Max Batch: {max_batch}\n'
              f'Min Batch: {min_batch}\n'
              f'Batches: {len(df)}')

plt.figtext(0.15, 0.85, stats_text, 
            bbox={"facecolor":"lightyellow", "alpha":0.9, "pad":5})

# Adjust layout and save
plt.tight_layout()
plt.savefig('tweets_per_batch.png', dpi=300, bbox_inches='tight')

# Show the plot
plt.show()

print(f"Plot saved as 'tweets_per_batch.png'")