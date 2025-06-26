import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os
from datetime import datetime

# File paths
folder_path = 'c:\\Users\\antek\\Desktop\\projekt_io\\compare_with_poll'
polls_file = os.path.join(folder_path, 'poll_nawrocki_trzaskowski_2025.csv')
nawrocki_emotions_file = os.path.join(folder_path, 'nawrocki_daily_emotions.csv')
trzaskowski_emotions_file = os.path.join(folder_path, 'trzaskowski_daily_emotions.csv')

# Load the data
polls_df = pd.read_csv(polls_file)
nawrocki_emotions_df = pd.read_csv(nawrocki_emotions_file)
trzaskowski_emotions_df = pd.read_csv(trzaskowski_emotions_file)

# Handle the "Election Day" entry
election_day_index = polls_df[polls_df['start_date'] == 'Election Day'].index.tolist()
if election_day_index:
    polls_df.loc[election_day_index, 'start_date'] = '1 June 2025'
    polls_df.loc[election_day_index, 'end_date'] = '1 June 2025'
    is_election_day = True
else:
    is_election_day = False

# Convert date columns
polls_df['start_date'] = pd.to_datetime(polls_df['start_date'], format='%d %b %Y')
polls_df['end_date'] = pd.to_datetime(polls_df['end_date'], format='%d %b %Y')

# Convert datetime in emotion dataframes, handling timezone info
nawrocki_emotions_df['datetime'] = pd.to_datetime(nawrocki_emotions_df['datetime']).dt.tz_localize(None)
trzaskowski_emotions_df['datetime'] = pd.to_datetime(trzaskowski_emotions_df['datetime']).dt.tz_localize(None)

# Scale poll support from 0-100 to -1 to 1
polls_df['nawrocki_scaled'] = (polls_df['nawrocki'] / 50) - 1
polls_df['trzaskowski_scaled'] = (polls_df['trzaskowski'] / 50) - 1

# Calculate average emotions for each candidate (for use as default values)
nawrocki_valid_emotions = nawrocki_emotions_df[nawrocki_emotions_df['sentiment_count'] > 0]
trzaskowski_valid_emotions = trzaskowski_emotions_df[trzaskowski_emotions_df['sentiment_count'] > 0]

# Calculate weighted averages
if len(nawrocki_valid_emotions) > 0:
    nawrocki_avg_emotion = np.average(
        nawrocki_valid_emotions['numeric_score'], 
        weights=nawrocki_valid_emotions['sentiment_count']
    )
else:
    nawrocki_avg_emotion = 0

if len(trzaskowski_valid_emotions) > 0:
    trzaskowski_avg_emotion = np.average(
        trzaskowski_valid_emotions['numeric_score'], 
        weights=trzaskowski_valid_emotions['sentiment_count']
    )
else:
    trzaskowski_avg_emotion = 0

# Function to group emotion data by poll periods
def group_emotions_by_poll_period(emotions_df, polls_df, default_emotion):
    """Group daily emotion data to match the weekly poll periods."""
    grouped_emotions = []
    
    for _, poll_row in polls_df.iterrows():
        start_date = poll_row['start_date']
        end_date = poll_row['end_date']
        
        # Filter emotions that fall within this poll period
        period_emotions = emotions_df[
            (emotions_df['datetime'] >= start_date) & 
            (emotions_df['datetime'] <= end_date)
        ]
        
        # Calculate average sentiment for the period
        valid_emotions = period_emotions[period_emotions['sentiment_count'] > 0]
        if len(valid_emotions) > 0:
            # Weighted average by sentiment_count
            weighted_avg = np.average(
                valid_emotions['numeric_score'], 
                weights=valid_emotions['sentiment_count']
            )
            grouped_emotions.append(weighted_avg)
        else:
            # Use default emotion when no data is available
            grouped_emotions.append(default_emotion)
    
    return grouped_emotions

# Group emotions by poll periods
nawrocki_grouped_emotions = group_emotions_by_poll_period(nawrocki_emotions_df, polls_df, nawrocki_avg_emotion)
trzaskowski_grouped_emotions = group_emotions_by_poll_period(trzaskowski_emotions_df, polls_df, trzaskowski_avg_emotion)

# Add grouped emotions to polls dataframe
polls_df['nawrocki_emotions'] = nawrocki_grouped_emotions
polls_df['trzaskowski_emotions'] = trzaskowski_grouped_emotions

# Create a date for x-axis that represents the middle of each poll period
polls_df['mid_date'] = polls_df['start_date'] + (polls_df['end_date'] - polls_df['start_date']) / 2

# Define key events
nawrocki_events = [
    {"label": "Mieszkanie (05.05.2025)", "date": "2025-05-05", "color": "red"},
    {"label": "Snus (23.05.2025)", "date": "2025-05-23", "color": "orange"},
    {"label": "Rozmowa (22.05.2025)", "date": "2025-05-22", "color": "green"}
]
    
trzaskowski_events = [
    {"label": "Debata (11.04.2025)", "date": "2025-04-11", "color": "blue"},
    {"label": "NASK (15.05.2025)", "date": "2025-05-15", "color": "green"},
    {"label": "Obietnica (20.05.2025)", "date": "2025-05-20", "color": "red"}
]

# Convert event dates to datetime
for event in nawrocki_events:
    event["date"] = pd.to_datetime(event["date"])
    
for event in trzaskowski_events:
    event["date"] = pd.to_datetime(event["date"])

# Function to add events to plot
def add_events_to_plot(ax, events):
    for i, event in enumerate(events):
        ax.axvline(x=event["date"], color=event["color"], linestyle='--', alpha=0.7)
        # Place text labels at alternating heights to avoid overlap
        y_pos = 0.9 - (i % 3) * 0.15
        ax.text(event["date"], y_pos, event["label"], 
                rotation=90, verticalalignment='top', horizontalalignment='right',
                fontsize=10, color=event["color"])

# Create plot for Nawrocki
plt.figure(figsize=(15, 8))
plt.plot(polls_df['mid_date'], polls_df['nawrocki_scaled'], 'b-', marker='o', linewidth=2, 
         markersize=8, label='Poll Support')
plt.plot(polls_df['mid_date'], polls_df['nawrocki_emotions'], 'r-', marker='x', linewidth=2, 
         markersize=8, label='Sentiment')
plt.title('Nawrocki - Poll Support vs Sentiment', fontsize=18, pad=15)
plt.ylabel('Score (-1 to 1)', fontsize=14)
plt.xlabel('Date', fontsize=14)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=14)
plt.ylim(-1.1, 1.1)
plt.axhline(y=0, color='k', linestyle='-', alpha=0.2)

# Add events to Nawrocki plot
add_events_to_plot(plt.gca(), nawrocki_events)

# Mark Election Day if it exists
if is_election_day:
    election_idx = polls_df.index[-1]
    plt.axvline(x=polls_df.loc[election_idx, 'mid_date'], color='black', linestyle='--', alpha=0.7)
    plt.text(polls_df.loc[election_idx, 'mid_date'], 0.9, 'Election Day', 
             rotation=90, verticalalignment='top', fontsize=12)

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
plt.xticks(fontsize=12, rotation=45)
plt.yticks(fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(folder_path, 'nawrocki_comparison.png'), dpi=300, bbox_inches='tight')
plt.close()

# Create plot for Trzaskowski
plt.figure(figsize=(15, 8))
plt.plot(polls_df['mid_date'], polls_df['trzaskowski_scaled'], 'g-', marker='o', linewidth=2, 
         markersize=8, label='Poll Support')
plt.plot(polls_df['mid_date'], polls_df['trzaskowski_emotions'], 'r-', marker='x', linewidth=2, 
         markersize=8, label='Sentiment')
plt.title('Trzaskowski - Poll Support vs Sentiment', fontsize=18, pad=15)
plt.xlabel('Date', fontsize=14)
plt.ylabel('Score (-1 to 1)', fontsize=14)
plt.grid(True, alpha=0.3)
plt.legend(fontsize=14)
plt.ylim(-1.1, 1.1)
plt.axhline(y=0, color='k', linestyle='-', alpha=0.2)

# Add events to Trzaskowski plot
add_events_to_plot(plt.gca(), trzaskowski_events)

# Mark Election Day if it exists
if is_election_day:
    election_idx = polls_df.index[-1]
    plt.axvline(x=polls_df.loc[election_idx, 'mid_date'], color='black', linestyle='--', alpha=0.7)
    plt.text(polls_df.loc[election_idx, 'mid_date'], 0.9, 'Election Day', 
             rotation=90, verticalalignment='top', fontsize=12)

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
plt.xticks(fontsize=12, rotation=45)
plt.yticks(fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(folder_path, 'trzaskowski_comparison.png'), dpi=300, bbox_inches='tight')
plt.show()