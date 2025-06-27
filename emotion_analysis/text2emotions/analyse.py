from transformers import MarianMTModel, MarianTokenizer
import text2emotion as te
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import os 
import sys
import re

model_name = "Helsinki-NLP/opus-mt-pl-en"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)


def clean_tweet(tweet):

  tweet = str(tweet)
  tweet = re.sub(r'http\S+|www\S+|https\S+', '', tweet, flags=re.MULTILINE)
  tweet = re.sub(r'\@\w+|\#', '', tweet)
  return tweet


def translate_pl_to_eng(text):
  inputs = tokenizer(text, return_tensors="pt", padding=True)
  output = model.generate(**inputs)
  return tokenizer.decode(output[0], skip_special_tokens=True)


def analyze_tweets_emotions(df):
  emotion_columns = ['Happy', 'Angry', 'Surprise', 'Sad', 'Fear']

  for col in emotion_columns:
    df[col] = 0.0

  for i in tqdm(range(len(df))):
    if 'Text' in df.columns:
      text = df.iloc[i]['Text']
    else:
      text = df.iloc[i,2]

    try:
      cleaned_text = clean_tweet(text)

      if not cleaned_text or len(cleaned_text) < 5:
        continue
        
      # Translate to English
      translated_text = translate_pl_to_eng(cleaned_text)
      
      # Get raw emotions
      emotions = te.get_emotion(translated_text)
      
      # Store each emotion directly
      for emotion, score in emotions.items():
        df.loc[df.index[i], emotion] = score
    except Exception as e:
      print(f"Error processing tweet {i}: {e}")

  return df


def calculate_daily_emotions(df):
  # Make sure datetime column exists
  if 'Created_At' in df.columns:
    df['datetime'] = pd.to_datetime(df['Created_At'])
  
  # Group by day and calculate mean of each emotion
  emotion_columns = ['Happy', 'Angry', 'Surprise', 'Sad', 'Fear']
  daily_emotions = df.groupby(pd.Grouper(key="datetime", freq="D")).agg({
    **{emotion: 'mean' for emotion in emotion_columns},
    'Text': 'count'
  }).rename(columns={"Text": "tweet_count"})
  
  # Fill NaN values with 0
  daily_emotions = daily_emotions.fillna(0)
  
  return daily_emotions

def plot_emotion_timeline(daily_emotions, key_events, title, output_path):
  """Plot multiple emotion timelines with key events"""
  plt.figure(figsize=(15, 8))
  
  # Plot each emotion with a different color
  plt.plot(daily_emotions.index, daily_emotions['Happy'], 'g-', linewidth=2, label='Happy')
  plt.plot(daily_emotions.index, daily_emotions['Sad'], 'b-', linewidth=2, label='Sad')
  plt.plot(daily_emotions.index, daily_emotions['Angry'], 'r-', linewidth=2, label='Angry')
  plt.plot(daily_emotions.index, daily_emotions['Fear'], 'k-', linewidth=2, label='Fear')
  plt.plot(daily_emotions.index, daily_emotions['Surprise'], 'y-', linewidth=2, label='Surprise')
  
  # Add tweet count as area plot
  plt.fill_between(daily_emotions.index, 0, 
                  daily_emotions['tweet_count'] / daily_emotions['tweet_count'].max() * 0.2,
                  alpha=0.2, color='gray', label='Tweet Volume (scaled)')
  
  # Add key events as vertical lines
  for event in key_events:
    event_date = pd.to_datetime(event["date"])
    plt.axvline(x=event_date, color=event["color"], linestyle='--', alpha=0.7)
    plt.text(event_date, 0.9, event["label"], rotation=90, 
             verticalalignment='top', fontsize=10)
  
  # Set labels and title
  plt.xlabel('Date')
  plt.ylabel('Emotion Score')
  plt.title(title)
  plt.legend()
  plt.grid(True, linestyle='--', alpha=0.7)
  
  # Save the figure
  plt.tight_layout()
  plt.savefig(output_path)
  plt.show()

def load_event_tweets(event_path):
  """Load tweets from a specific event folder, only latest tweets."""
  all_csv_files = []

  # Check if the directory exists
  if not os.path.exists(event_path):
    print(f"Error: Directory {event_path} does not exist.")
    return None

  # Get all CSV files in the directory (not recursive)
  for file in os.listdir(event_path):
    if file.endswith(".csv"):
      # Only include files with "latest" in the name, exclude "top" tweets
      if "latest" in file.lower() and "top" not in file.lower():
        all_csv_files.append(os.path.join(event_path, file))

  print(f"Found {len(all_csv_files)} CSV files in {event_path}")

  all_tweets = pd.DataFrame()

  for file_path in tqdm(all_csv_files, desc="Loading files"):
    try:
      df = pd.read_csv(file_path)
      # Add event name as source
      df['source'] = os.path.basename(event_path)
      all_tweets = pd.concat([all_tweets, df], ignore_index=True)
    except Exception as e:
      print(f"Error loading {file_path}: {e}")

  if not all_tweets.empty and 'Created_At' in all_tweets.columns:
    # Convert Created_At to datetime
    all_tweets['datetime'] = pd.to_datetime(all_tweets['Created_At'], 
                                          format='%a %b %d %H:%M:%S %z %Y', 
                                          errors='coerce')
    
    # Drop invalid dates
    all_tweets = all_tweets.dropna(subset=['datetime'])
    
    # Sort by date
    all_tweets = all_tweets.sort_values('datetime')

  return all_tweets

def main():
  # Set paths to specific event folders
  nawrocki_snus_dir = 'c:/Users/antek/Desktop/projekt_io/momenty_nawrocki/snus'
  trzaskowski_debata_dir = 'c:/Users/antek/Desktop/projekt_io/momenty_trzaskowski/debata'

  # Define key events for each candidate (you can simplify to just these specific events)
  nawrocki_events = [
    {"label": "Snus (23.05.2025)", "date": "2025-05-23", "color": "orange"}
  ]
    
  trzaskowski_events = [
    {"label": "Debata (11.04.2025)", "date": "2025-04-11", "color": "blue"}
  ]

  # Create output directory
  output_dir = 'text2emotion_specific_events'
  os.makedirs(output_dir, exist_ok=True)

  # Process Nawrocki snus tweets
  print("Processing Nawrocki snus tweets...")
  nawrocki_tweets = load_event_tweets(nawrocki_snus_dir)
  
  if nawrocki_tweets is not None and not nawrocki_tweets.empty:
    # Analyze emotions using text2emotion
    print("Analyzing emotions in Nawrocki snus tweets...")
    nawrocki_with_emotions = analyze_tweets_emotions(nawrocki_tweets)
    
    # Calculate daily emotions
    print("Calculating daily emotions for Nawrocki snus...")
    daily_emotions_nawrocki = calculate_daily_emotions(nawrocki_with_emotions)
    
    # Save to CSV
    daily_emotions_nawrocki.to_csv(f'{output_dir}/nawrocki_snus_emotions.csv')
    
    # Plot timeline
    print("Creating emotion timeline for Nawrocki snus...")
    plot_emotion_timeline(
      daily_emotions_nawrocki,
      nawrocki_events,
      'Text2Emotion Analysis of Tweets about Nawrocki Snus Event',
      f'{output_dir}/nawrocki_snus_timeline.png'
    )
  else:
    print("No valid tweets found for Nawrocki snus event.")

  # Process Trzaskowski debata tweets
  print("Processing Trzaskowski debata tweets...")
  trzaskowski_tweets = load_event_tweets(trzaskowski_debata_dir)
  
  if trzaskowski_tweets is not None and not trzaskowski_tweets.empty:
    # Analyze emotions using text2emotion
    print("Analyzing emotions in Trzaskowski debata tweets...")
    trzaskowski_with_emotions = analyze_tweets_emotions(trzaskowski_tweets)
    
    # Calculate daily emotions
    print("Calculating daily emotions for Trzaskowski debata...")
    daily_emotions_trzaskowski = calculate_daily_emotions(trzaskowski_with_emotions)
    
    # Save to CSV
    daily_emotions_trzaskowski.to_csv(f'{output_dir}/trzaskowski_debata_emotions.csv')
    
    # Plot timeline
    print("Creating emotion timeline for Trzaskowski debata...")
    plot_emotion_timeline(
      daily_emotions_trzaskowski,
      trzaskowski_events,
      'Text2Emotion Analysis of Tweets about Trzaskowski Debata Event',
      f'{output_dir}/trzaskowski_debata_timeline.png'
    )
  else:
    print("No valid tweets found for Trzaskowski debata event.")
    
  print("Analysis complete! Results saved to the text2emotion_specific_events directory.")
  # Set directory paths for tweets
  nawrocki_dir = 'c:/Users/antek/Desktop/projekt_io/momenty_nawrocki/snus'
  trzaskowski_dir = 'c:/Users/antek/Desktop/projekt_io/momenty_trzaskowski/debata'

  # Define key events for each candidate
  nawrocki_events = [
    {"label": "Snus (23.05.2025)", "date": "2025-05-23", "color": "orange"},
  ]
    
  trzaskowski_events = [
    {"label": "Debata (11.04.2025)", "date": "2025-04-11", "color": "blue"},
  ]

  # Process Nawrocki tweets
  print("Processing Nawrocki tweets...")
  nawrocki_tweets = load_event_tweets(nawrocki_dir)
  
  if nawrocki_tweets is not None:
    # Analyze emotions using text2emotion
    print("Analyzing emotions in Nawrocki tweets...")
    nawrocki_with_emotions = analyze_tweets_emotions(nawrocki_tweets)
    
    # Calculate daily emotions
    print("Calculating daily emotions for Nawrocki...")
    daily_emotions_nawrocki = calculate_daily_emotions(nawrocki_with_emotions)
    
    # Save to CSV
    output_dir = 'text2emotion_results'
    os.makedirs(output_dir, exist_ok=True)
    daily_emotions_nawrocki.to_csv(f'{output_dir}/nawrocki_daily_emotions_text2emotion.csv')
    
    # Plot timeline
    print("Creating emotion timeline for Nawrocki...")
    plot_emotion_timeline(
      daily_emotions_nawrocki,
      nawrocki_events,
      'Text2Emotion Analysis of Tweets about Karol Nawrocki',
      f'{output_dir}/nawrocki_text2emotion_timeline.png'
    )

  # Process Trzaskowski tweets
  print("Processing Trzaskowski tweets...")
  trzaskowski_tweets = load_event_tweets(trzaskowski_dir)
  
  if trzaskowski_tweets is not None:
    # Analyze emotions using text2emotion
    print("Analyzing emotions in Trzaskowski tweets...")
    trzaskowski_with_emotions = analyze_tweets_emotions(trzaskowski_tweets)
    
    # Calculate daily emotions
    print("Calculating daily emotions for Trzaskowski...")
    daily_emotions_trzaskowski = calculate_daily_emotions(trzaskowski_with_emotions)
    
    # Save to CSV
    daily_emotions_trzaskowski.to_csv(f'{output_dir}/trzaskowski_daily_emotions_text2emotion.csv')
    
    # Plot timeline
    print("Creating emotion timeline for Trzaskowski...")
    plot_emotion_timeline(
      daily_emotions_trzaskowski,
      trzaskowski_events,
      'Text2Emotion Analysis of Tweets about Rafał Trzaskowski',
      f'{output_dir}/trzaskowski_text2emotion_timeline.png'
    )
    
  print("Analysis complete! Results saved to the text2emotion_results directory.")

if __name__ == "__main__":
  main()
