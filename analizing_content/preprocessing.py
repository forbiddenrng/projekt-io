import pandas as pd
import re
import json
import nltk
from nltk.tokenize import word_tokenize
import morfeusz2

nltk.download('punkt_tab')

"""
Remove links from and special characters like mentioning (@) and hashtags (#) from the tweet
"""
def clean_tweet(tweet):

  tweet = str(tweet)
  tweet = re.sub(r'http\S+|www\S+|https\S+', '', tweet, flags=re.MULTILINE)
  tweet = re.sub(r'\@\w+|\#', '', tweet)
  return tweet


def load_stop_words(file_path='stop_words_polish.json'):
  try:
    with open(file_path, 'r', encoding='utf-8') as file:
      stop_words = json.load(file)
    return stop_words
  except Exception as e:
    print(f"Error loading stop words: {e}")
    return []

def preprocess_tweets(tweets):
  cleaned_tweets = []

  stop_words = load_stop_words()
  morf = morfeusz2.Morfeusz()

  for tweet in tweets:
    tweet = clean_tweet(tweet)
    tokens = word_tokenize(tweet.lower())

    tokens = [morf.analyse(word)[0][2][1] for word in tokens if word.isalpha() and word not in stop_words]
    cleaned_tweets.extend(tokens)

  return cleaned_tweets


def get_word_frequency(tokens):
  return pd.Series(tokens).value_counts()


# def main():
#   tweets = [
#     "@HTDx64 @damiani_28 No nie zostanie kandydat Rosji bo Trzaskowski przegrał wybory.",
#     "@MorawieckiM Znaczy , że jeżeli tzw. pomyłki dotyczyły 184 tys 796 osób, to wybory zwyciężył Rafał Trzaskowski i tego się boisz."
#   ]

#   result = preprocess_tweets(tweets)
#   print(len(result))



# main()
