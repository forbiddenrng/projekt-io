import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import glob
from datetime import datetime

# Base directory containing all tweet files
base_dir = 'c:/Users/antek/Desktop/projekt_io/momenty_nawrocki'

# Find all CSV files in the directory and subdirectories
csv_files = []
for root, dirs, files in os.walk(base_dir):
  for file in files:
    if file.endswith('.csv'):
      csv_files.append(os.path.join(root, file))

print(f"Found {len(csv_files)} CSV files")

# Read all CSV files and combine them
all_tweets = []
for file in csv_files:
  try:
    # Read CSV file
    df = pd.read_csv(file, encoding='utf-8')
    
    # Check if required columns exist
    if 'Created_At' in df.columns:
      # Determine source based on directory
      relative_path = os.path.relpath(file, base_dir)
      parts = relative_path.split(os.sep)
      
      if len(parts) > 1:
          # It's in a subdirectory
          df['source'] = parts[0]
      else:
          # It's in the main directory
          df['source'] = 'main'
          
      all_tweets.append(df)
  except Exception as e:
    print(f"Error reading {file}: {e}")

# Combine all DataFrames
if all_tweets:
    combined_df = pd.concat(all_tweets, ignore_index=True)
    
    # Convert Created_At to datetime
    combined_df['datetime'] = pd.to_datetime(combined_df['Created_At'], format='%a %b %d %H:%M:%S %z %Y', errors='coerce')

    # Drop rows with invalid dates
    combined_df = combined_df.dropna(subset=['datetime'])
    
    # Sort by date
    combined_df = combined_df.sort_values('datetime')
    
    # Create figure and plot
    plt.figure(figsize=(15, 8))
    
    # Group sources into categories
    main_sources = ['mieszkanie', 'snus']
    colors = {'mieszkanie': 'red', 'snus': 'green', 'main': 'purple'}
    
    # Plot by source categories
    for source in combined_df['source'].unique():
      source_df = combined_df[combined_df['source'] == source]
      tweets_by_day = source_df.groupby(pd.Grouper(key='datetime', freq='D')).size()
      color = colors.get(source, 'gray')
      plt.plot(tweets_by_day.index, tweets_by_day.values, 
                label=source, color=color, alpha=0.7)
    
    # Plot total tweets
    tweets_by_day_total = combined_df.groupby(pd.Grouper(key='datetime', freq='D')).size()
    plt.plot(tweets_by_day_total.index, tweets_by_day_total.values, 
             'k-', label='Total', linewidth=2.5)
    
    # Mark important events
    events = [
        {"date": "2025-04-30", "label": "Mieszkanie", "color": "red"},
        {"date": "2025-05-23", "label": "Snus", "color": "red"},
    ]
    
    for i, event in enumerate(events):
      event_date = pd.to_datetime(event["date"])
      plt.axvline(x=event_date, color=event["color"], linestyle='--', alpha=0.7, linewidth=1.5)
      
      # Add text with proper positioning to avoid overlap
      y_max = plt.ylim()[1]
      offset = 0.1 * (i % 3)  # Stagger the labels
      plt.annotate(event["label"], xy=(event_date, y_max * (0.95 - offset)),
                  xytext=(10, 0), textcoords='offset points',
                  rotation=90, va='top', ha='left',
                  color=event["color"], fontweight='bold')
    
    # Format the plot
    plt.title('Tweets about Karol Nawrocki during 2025 Election Campaign', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Number of Tweets per Day', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left')
    
    # Format x-axis dates
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    
    # Save the figure
    output_path = os.path.join(base_dir, 'nawrocki_tweets_timeline2.png')
    plt.savefig(output_path, dpi=300)
    print(f"Plot saved to: {output_path}")
    
    plt.show()
    
    print(f"Total tweets analyzed: {len(combined_df)}")
    print(f"Date range: {combined_df['datetime'].min().date()} to {combined_df['datetime'].max().date()}")
else:
  print("No valid CSV files found.")