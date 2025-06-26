import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys
import json
import datetime as datetime
import numpy as np
from tqdm import tqdm
import random
import torch

seed=42
random.seed(seed)
np.random.seed(seed)
if torch.cuda.is_available():
  torch.cuda.manual_seed_all(seed)

##add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analizing_content.preprocessing import clean_tweet
from analizing_content.data_loading import load_all_tweets

from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer, AutoModel

model_name = "citizenlab/twitter-xlm-roberta-base-sentiment-finetunned"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
sentiment_analyzer = pipeline("text-classification", model=model, tokenizer=tokenizer)





def analyze_emotion(text):
  try:
    cleaned_text = clean_tweet(text)
    if not cleaned_text or len(cleaned_text) < 5:
      return {"score": 0, "label": "NEUTRAL"}

    if len(cleaned_text) > 512:
      cleaned_text = cleaned_text[:512]

    result = sentiment_analyzer(cleaned_text)[0]

    # if result['label'] == 'LABEL_0':
    #   result['label'] = 'NEGATIVE'
    # elif result['label'] == 'LABEL_1':
    #   result['label'] = 'POSITIVE'
    if result['label'] == 'Positive':
      result['label'] = 'POSITIVE'
    elif result['label'] == 'Negative':
      result['label'] = 'NEGATIVE'
    elif result['label'] == 'Neutral':
      result['label'] == 'NEUTRAL'

    
    return result

    # return result
  except Exception as e:
    print(f"Error anayzling text: {e}")
    return {"score": 0, "label": "NEUTRAL"}




wypowiedzi = [
  "W końcu ktoś zabrał się za realną reformę sądownictwa. Brawo dla rządu za odwagę!",
  "Dzięki programom socjalnym wielu rodzinom żyje się po prostu lepiej. To jest realna pomoc, a nie tylko obietnice.",
  "Po raz pierwszy od lat czuję, że Polska ma konkretną strategię energetyczną. Inwestycje w atom i OZE idą w dobrym kierunku.",
  "Duży plus za walkę z wykluczeniem komunikacyjnym. Pociągi wracają do małych miejscowości. Tak trzymać!",
  "Fajnie widzieć, że Polska potrafi prowadzić niezależną politykę zagraniczną i stawiać własne interesy na pierwszym miejscu.",
  "Obiecali transparentność, a mamy jeszcze większy chaos i układy niż wcześniej. Zero zaufania.",
  "Kolejna afera i żadnych konsekwencji. Czy ktokolwiek jeszcze wierzy w uczciwość tej władzy?",
  "Młodzi wyjeżdżają, bo nie widzą tu przyszłości. Gdzie są reformy, które miały zatrzymać emigrację?",
  "Rolnicy protestują, a rząd udaje, że wszystko jest OK. Ignorancja wobec wsi to katastrofa.",
  "Politycy przejmują media publiczne jak swoją własność. To już nie informacja, tylko propaganda."
]


def analyze_sample_statements(statements):
  for statement in statements:
    print(analyze_emotion(statement))

# analyze_sample_statements(wypowiedzi)




def load_condidate_tweets(base_dir):
  all_csv_files = []

  for root, dirs, files in os.walk(base_dir):
    for file in files:
      exclude_files = ["top_po.csv", "top_przed.csv"]
      if file.endswith(".csv") and file not in exclude_files:
        all_csv_files.append(os.path.join(root, file))

  print(f"Found {len(all_csv_files)} CSV files in {base_dir}")

  all_tweets = pd.DataFrame()

  for file_path in tqdm(all_csv_files, desc="Loading files"):
    try:
      source = os.path.basename(os.path.dirname(file_path))\
      
      df = pd.read_csv(file_path)

      df['source'] = source

      all_tweets = pd.concat([all_tweets, df], ignore_index=True)
    except Exception as e:
      print(f"Error loading {file_path}: {e}")

  if not all_tweets.empty and 'Created_At' in all_tweets.columns:
    #conver Created_At to datetime
    all_tweets['datetime'] = pd.to_datetime(all_tweets['Created_At'], 
                                            format='%a %b %d %H:%M:%S %z %Y', 
                                            errors='coerce')
    
    #drop invalid dates
    all_tweets = all_tweets.dropna(subset=['datetime'])

    # sort by date
    all_tweets = all_tweets.sort_values('datetime')

  return all_tweets


def analyze_tweets_emotions(df):
  
  df['emotion_score'] = 0.0
  df['emotion_label'] = 'NEUTRAL'

  for i in tqdm(range(len(df))):
    if 'Text' in df.columns:
      text = df.iloc[i]['Text']
    else:
      text = df.iloc[i,2]

    result = analyze_emotion(text)

    df.loc[df.index[i], 'emotion_score'] = result['score']
    df.loc[df.index[i], 'emotion_label'] = result['label']

  return df


def calculate_daily_emotions(df):
  df['numeric_score'] = df.apply(
    lambda row: row['emotion_score'] if row['emotion_label'] == 'POSITIVE' 
                else -row['emotion_score'] if row['emotion_label'] == 'NEGATIVE' 
                else 0,
    axis=1 
  )

  # Count sentiment tweets (positive and negative only)
  df['is_sentiment'] = df['emotion_label'].isin(['POSITIVE', 'NEGATIVE']).astype(int)

  ## group by day
  daily_emotions = df.groupby(pd.Grouper(key="datetime", freq="D")).agg({
    'numeric_score': 'sum',
    'is_sentiment': 'sum',
    'Text': 'count'
  }).rename(columns={"Text": "tweet_count", "is_sentiment": "sentiment_count"})

  # sum of values (-1 and 1) where sentiment_count > 0 and divide by sentiment_count
  daily_emotions['numeric_score'] = daily_emotions['numeric_score'].where(daily_emotions['sentiment_count'] > 0, 0)
 

  if daily_emotions['numeric_score'].abs().max() > 0:
    max_abs_score = daily_emotions['numeric_score'].abs().max()
    daily_emotions['numeric_score'] = daily_emotions['numeric_score'] / max_abs_score


  return daily_emotions

def plot_emotion_timeline(daily_emotions, key_events, title, output_path):
    """Plot the emotion timeline with key events"""
    plt.figure(figsize=(15, 8))
    
    # Plot emotions
    plt.plot(daily_emotions.index, daily_emotions['numeric_score'], 
             'b-', linewidth=2, label='Sentiment Score')
    
    # Add tweet count as area plot
    plt.fill_between(daily_emotions.index, 0, 
                     daily_emotions['tweet_count'] / daily_emotions['tweet_count'].max() * 0.5,
                     alpha=0.3, color='gray', label='Tweet Volume (scaled)')
    
    # Add zero line
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    # Add key events
    for event in key_events:
        event_date = pd.to_datetime(event["date"])
        plt.axvline(x=event_date, color=event["color"], linestyle='--', alpha=0.7)
        
        # Add annotation
        plt.annotate(event["label"], 
                    xy=(event_date, -0.5), 
                    xytext=(10, 0), textcoords='offset points',
                    rotation=90, va='top', ha='left',
                    color=event["color"], fontweight='bold')
    
    # Format the plot
    plt.title(title, fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Average Sentiment (Negative to Positive)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left')
    
    # Format x-axis dates
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.xticks(rotation=45)
    
    # Set y-axis limits
    plt.ylim(-1, 1)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"Plot saved to: {output_path}")
    
    plt.show()


def main():
  nawrocki_dir = 'c:/Users/antek/Desktop/projekt_io/momenty_nawrocki'
  trzaskowski_dir = 'c:/Users/antek/Desktop/projekt_io/momenty_trzaskowski'

  # key events
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


  print("Processing Nawrocki tweets...")

  nawrocki_tweets = load_condidate_tweets(nawrocki_dir)

  if nawrocki_tweets is not None:
    nawrocki_with_emotions = analyze_tweets_emotions(nawrocki_tweets)
    daily_emotions_nawrocki = calculate_daily_emotions(nawrocki_with_emotions)


    # Save processed data
    # nawrocki_with_emotions.to_csv('nawrocki_tweets_with_emotions.csv', index=False)
    daily_emotions_nawrocki.to_csv('nawrocki_daily_emotions.csv')

    #plot timeline

    plot_emotion_timeline(
      daily_emotions_nawrocki,
      nawrocki_events,
      'Emotion Analysis of Tweets about Karol Nawrocki',
      'nawrocki_emotion_timeline.png'
    )

  print("Processing Trzaskowski tweets...")

  trzaskowski_tweets = load_condidate_tweets(trzaskowski_dir)

  if trzaskowski_tweets is not None:
    trzaskowski_with_emotions = analyze_tweets_emotions(trzaskowski_tweets)
    daily_emotions_trzaskowski = calculate_daily_emotions(trzaskowski_with_emotions)


    # Save processed data
    # trzaskowski_with_emotions.to_csv('trzaskowski_tweets_with_emotions.csv', index=False)
    daily_emotions_trzaskowski.to_csv('trzaskowski_daily_emotions.csv')

    #plot timeline

    plot_emotion_timeline(
      daily_emotions_trzaskowski,
      trzaskowski_events,
      'Emotion Analysis of Tweets about Rafał Trzaskowski',
      'trzaskowski_emotion_timeline.png'
    )


if __name__ == "__main__":
  main()
