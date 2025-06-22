import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import glob

# Paths to the tweet folders
debata_folder = "c:/Users/antek/Desktop/projekt_io/momenty_trzaskowski/debata"
nask_folder = "c:/Users/antek/Desktop/projekt_io/momenty_trzaskowski/nask"
obietnica_folder = "c:/Users/antek/Desktop/projekt_io/momenty_trzaskowski/obietnica"

# Function to read all CSV files from a folder
def read_csv_files(folder_path):
    all_data = pd.DataFrame()
    for csv_file in glob.glob(os.path.join(folder_path, "*.csv")):
        try:
            # Read CSV file
            df = pd.read_csv(csv_file)
            all_data = pd.concat([all_data, df])
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")
    return all_data

# Read all tweets from both folders
print("Reading mieszkanie tweets...")
debata_tweets = read_csv_files(debata_folder)
print("Reading snus tweets...")
nask_tweets = read_csv_files(nask_folder)
print("Reading snus tweets...")
obietnica_tweets = read_csv_files(obietnica_folder)

# Combine all tweets
all_tweets = pd.concat([debata_tweets, nask_tweets, obietnica_tweets])

# Parse the Created_At dates (Twitter format: "Mon Apr 28 23:05:33 +0000 2025")
def parse_tweet_date(date_str):
    try:
        return datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
    except Exception as e:
        print(f"Error parsing date '{date_str}': {e}")
        return None

# Parse dates for all datasets
all_tweets['Date'] = all_tweets['Created_At'].apply(parse_tweet_date)
debata_tweets['Date'] = debata_tweets['Created_At'].apply(parse_tweet_date)
nask_tweets['Date'] = nask_tweets['Created_At'].apply(parse_tweet_date)
obietnica_tweets['Date'] = obietnica_tweets['Created_At'].apply(parse_tweet_date)

# Remove tweets with invalid dates
all_tweets = all_tweets.dropna(subset=['Date'])
debata_tweets = debata_tweets.dropna(subset=['Date'])
nask_tweets = nask_tweets.dropna(subset=['Date'])
obietnica_tweets = obietnica_tweets.dropna(subset=['Date'])

print(f"Total valid tweets: {len(all_tweets)}")

# Count tweets per day
tweets_per_day = all_tweets.groupby(all_tweets['Date'].dt.date).size().reset_index(name='count')
tweets_per_day['Date'] = pd.to_datetime(tweets_per_day['Date'])

debata_per_day = debata_tweets.groupby(debata_tweets['Date'].dt.date).size().reset_index(name='count')
debata_per_day['Date'] = pd.to_datetime(debata_per_day['Date'])

nask_per_day = nask_tweets.groupby(nask_tweets['Date'].dt.date).size().reset_index(name='count')
nask_per_day['Date'] = pd.to_datetime(nask_per_day['Date'])

obietnica_per_day = obietnica_tweets.groupby(obietnica_tweets['Date'].dt.date).size().reset_index(name='count')
obietnica_per_day['Date'] = pd.to_datetime(obietnica_per_day['Date'])





# Define the key events
key_events = [
    {"name": "NASK/Finansowanie spotów (15.05.2025)", "date": pd.to_datetime("15.05.2025")},
    {"name": "Obietnica (20.05.2025)", "date": pd.to_datetime("2025-05-20")},
    {"name": "Debata w TVP(11.04.2025)", "date": pd.to_datetime("2025-04-11")},
]

# Create the plot
plt.figure(figsize=(14, 8))

# Plot tweets per day by category
plt.plot(debata_per_day['Date'], debata_per_day['count'], marker='o', markersize=5, 
         linestyle='-', linewidth=1.5, color='blue', alpha=0.7, label='Debata w TVP')
         
plt.plot(nask_per_day['Date'], nask_per_day['count'], marker='s', markersize=5, 
         linestyle='-', linewidth=1.5, color='green', alpha=0.7, label='NASK')

plt.plot(obietnica_per_day['Date'], obietnica_per_day['count'], marker='s', markersize=5, 
         linestyle='-', linewidth=1.5, color='red', alpha=0.7, label='Obietnica')
         
plt.plot(tweets_per_day['Date'], tweets_per_day['count'], marker='x', markersize=6, 
         linestyle='-', linewidth=2, color='black', alpha=0.8, label='Total')

# Add key events as vertical lines
for i, event in enumerate(key_events):
    color = 'red' if i == 0 else 'purple'
    plt.axvline(x=event["date"], color=color, linestyle='--', linewidth=2, alpha=0.7)
    
    # Find max y value for text positioning
    max_y = tweets_per_day['count'].max()
    
    # Add annotation
    plt.annotate(event["name"], 
                 xy=(event["date"], max_y * 0.5), 
                 xytext=(event["date"], max_y * 0.9),
                 rotation=90, va='top', ha='center', 
                 fontsize=12, fontweight='bold',
                 color=color,
                 bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=color, alpha=0.8))

# Format the plot
plt.title('Tweets about Rafał Trzaskowski during the 2025 Election Campaign', fontsize=16, fontweight='bold')
plt.xlabel('Date', fontsize=14)
plt.ylabel('Number of Tweets', fontsize=14)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=12, loc='upper left')

# Format the x-axis to show dates nicely
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))  # Show date every 5 days
plt.gcf().autofmt_xdate()  # Rotate date labels

# Save and show the plot
plt.tight_layout()
plt.savefig('trzaskowski_tweets_timeline2.png', dpi=300)
plt.show()