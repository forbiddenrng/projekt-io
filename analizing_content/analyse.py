import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
from PIL import Image
import os 
from preprocessing import get_word_frequency, preprocess_tweets
from data_loading import load_all_tweets

def create_word_cloud(words, output_path=None, background_color="white", width=800, height=400, max_words=200):
  text = ' '.join(words)

  wordcloud = WordCloud(
    background_color=background_color,
    width=width,
    height=height,
    max_words=max_words,
    contour_width=1,
    contour_color="steelblue",
    collocations=False
  ).generate(text)

  plt.figure(figsize=(10, 6))
  plt.imshow(wordcloud, interpolation='bilinear')
  plt.axis('off')
    
  # Save if output path is provided
  if output_path:
    plt.savefig(output_path, bbox_inches='tight')
    print(f"Word cloud saved to {output_path}")
  
  return wordcloud


def plot_word_frequency(words, top_n=20, output_path=None, figsize=(12,8)):
  word_freq = get_word_frequency(words)

  top_words = word_freq.head(top_n)

  fig, ax = plt.subplots(figsize=figsize)

  bars = ax.barh(top_words.index, top_words.values, color='skyblue')


  ## add value labels 
  for bar in bars:
    width = bar.get_width()
    ax.text(width + 0.5, bar.get_y() + bar.get_height()/2, f'{width:.0f}', ha='left', va='center')
  
  ax.set_xlabel("Frequency")
  ax.set_ylabel("Words")
  ax.set_title(f"Top {top_n} Most Frequent Words")

  plt.tight_layout()

  if output_path:
    plt.savefig(output_path, bbox_inches='tight')
    print(f"Frequency chart saved to {output_path}")

  return fig


def analyze_tweet_content(file_paths, wordcloud_output=None, frequency_chart_output=None):
  # Load tweets
  tweets_df = load_all_tweets(file_paths)
  
  if tweets_df is None or tweets_df.empty:
    print("No tweets loaded. Cannot continue analysis.")
    return None, None, None
  
  # Extract tweet text column (assuming it's named 'text' - adjust if needed)
  tweet_texts = tweets_df['Text'].tolist() if 'Text' in tweets_df.columns else tweets_df.iloc[:, 0].tolist()

  
  # Preprocess tweets
  processed_words = preprocess_tweets(tweet_texts)
  
  # Print some statistics
  print(f"Total tweets analyzed: {len(tweet_texts)}")
  print(f"Total words after preprocessing: {len(processed_words)}")
  print(f"Unique words: {len(set(processed_words))}")
  
  # Generate word cloud
  wc = create_word_cloud(processed_words, output_path=wordcloud_output)
  
  # Generate frequency chart
  fc = plot_word_frequency(processed_words, output_path=frequency_chart_output)
  
  return processed_words, wc, fc



def main():
  file_paths = [
    '../momenty_trzaskowski/obietnica/latest_po.csv',
    '../momenty_trzaskowski/obietnica/top_po.csv',
  ]

  words, wc, freq_chart = analyze_tweet_content(
    file_paths,
    wordcloud_output='wordcloud_po_clean.png',
    frequency_chart_output='word_frequency_po_clean.png',
  )

  plt.show()

main()