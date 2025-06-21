import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read the CSV file
df = pd.read_csv('fetch_timeline.csv')

# Calculate cumulative sum of tweets
df['cumulative_tweets'] = df['batch_tweet_count'].cumsum()

# Create the plot
plt.figure(figsize=(12, 6))
plt.plot(df['seconds'], df['cumulative_tweets'], 'b-', linewidth=2)
plt.scatter(df['seconds'], df['cumulative_tweets'], color='red', s=30, alpha=0.7)

# Add a trend line
z = np.polyfit(df['seconds'], df['cumulative_tweets'], 1)
p = np.poly1d(z)
plt.plot(df['seconds'], p(df['seconds']), "r--", alpha=0.7, linewidth=1)

# Add labels and title
plt.xlabel('Time (seconds)')
plt.ylabel('Cumulative Tweets Fetched')
plt.title('Tweet Fetching Progress Over Time')
plt.grid(True, linestyle='--', alpha=0.7)

# Annotate the final count
final_time = df['seconds'].iloc[-1]
final_count = df['cumulative_tweets'].iloc[-1]
plt.annotate(f'Total: {final_count} tweets',
             xy=(final_time, final_count),
             xytext=(final_time-300, final_count-50),
             arrowprops=dict(facecolor='black', shrink=0.05, width=1.5))

# Calculate and show fetch rate
fetch_rate = final_count / final_time
plt.figtext(0.5, 0.01, f'Average fetch rate: {fetch_rate:.2f} tweets per second', 
            ha='center', fontsize=10, bbox={"facecolor":"orange", "alpha":0.2, "pad":5})

# Save the plot
plt.savefig('tweets_over_time.png', dpi=300, bbox_inches='tight')

# Show the plot
plt.show()

print(f"Plot saved as 'tweets_over_time.png'")