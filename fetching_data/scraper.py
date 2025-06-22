from twikit import Client, TooManyRequests
import time
import asyncio
from datetime import datetime
import csv
from configparser import ConfigParser
from random import randint, random

FILEPATH="../momenty_nawrocki/rozmowa/latest_po2.csv"
PRODUCT="Latest"
MINIMUM_TWEETS = 1600
START_DATE='2025-05-22'
END_DATE='2025-05-27'
# QUERY = f'(Karol OR Nawrocki OR snus OR nikotyna) lang:pl until:{END_DATE} since:{START_DATE}'
QUERY = f'Nawrocki Mentzen (Nawrocki OR Mentzen OR deklaracja OR rozmowa) lang:pl until:{END_DATE} since:{START_DATE}'

QUERIES = [
  'Nawrocki Mentzen (Nawrocki OR Mentzen OR deklaracja OR rozmowa) lang:pl until:2025-05-24 since:2025-05-23',
  'Nawrocki Mentzen (Nawrocki OR Mentzen OR deklaracja OR rozmowa) lang:pl until:2025-05-25 since:2025-05-24',
  'Nawrocki Mentzen (Nawrocki OR Mentzen OR deklaracja OR rozmowa) lang:pl until:2025-05-26 since:2025-05-25',
  'Nawrocki Mentzen (Nawrocki OR Mentzen OR deklaracja OR rozmowa) lang:pl until:2025-05-27 since:2025-05-26'

]

MIN_WAIT_TIME=15
MAX_WAIT_TIME=26
READ_TWEET_PROBABILITY = 0.61

def get_query(tweet_count):
  # return QUERY
  idx = tweet_count // 400
  return QUERIES[min(idx, len(QUERIES)- 1)]

prev_num_tweets = 0
prev_tweets_data = []

def get_next_wait_time():
  wait_time = 0
  for tweet in prev_tweets_data:
    read_tweet = random() < READ_TWEET_PROBABILITY
    if read_tweet:
      text = tweet[2]
      word_count = len(text.split())
      wait_time += word_count * 0.21
  random_offset = randint(2, 7)
  return max(int(wait_time), MIN_WAIT_TIME) + random_offset

# wait_time_metrics = []


with open(FILEPATH, 'w', newline='', encoding='utf-8') as file:
  writer = csv.writer(file)
  writer.writerow(['No.', 'Username', 'Text', 'Created_At', 'Replies', 'Favourite_Count', 'View_Count'])

current_query = None

async def main():
  start_time = datetime.now()
  global current_query

  async def get_tweets(tweets, tweet_count):
    global current_query
    current_time = datetime.now()
    elapsed_seconds = (current_time - start_time).total_seconds()
    new_query = get_query(tweet_count)

    if tweets is None:
      print(f'{datetime.now()} - Getting tweets...')
      current_query = new_query
      tweets = await client.search_tweet(current_query, product=PRODUCT)
    else:
      wait_time = get_next_wait_time()

      # wait_time_metrics.append({
      #   'seconds': round(elapsed_seconds),
      #   'batch_tweet_count': len(prev_tweets_data),
      #   'wait_time': wait_time
      # })

      print(f'{datetime.now()} - Getting next tweets after {wait_time} seconds')
      await asyncio.sleep(wait_time)

      print(f'Current query: {current_query}')
      print(f'New query: {new_query}')
      if new_query != current_query:
        print(f'Switching to new query: {new_query}')
        current_query = new_query
        tweets = await client.search_tweet(new_query, product=PRODUCT)
      else:
        # clear the previous tweets data
        prev_tweets_data.clear()
        tweets = await tweets.next()
    
    return tweets


  client = Client(language='en-US')

  client.load_cookies('cookies.json')

  tweet_count = 0
  tweets = None

  while tweet_count < MINIMUM_TWEETS:

    try:
      tweets = await get_tweets(tweets, tweet_count)
    except TooManyRequests as e:
      rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
      print(f'{datetime.now()} - Rate limit reached. Waiting until {rate_limit_reset}')
      wait_time = rate_limit_reset - datetime.now()

      # time.sleep(wait_time.total_seconds())
      await asyncio.sleep(wait_time.total_seconds())
      continue

    if not tweets:
      print(f'{datetime.now()} - No more tweets found')
      break

    for tweet in tweets:
      tweet_count += 1
      tweet_data = [tweet_count, tweet.user.name, tweet.text, tweet.created_at, tweet.reply_count,tweet.favorite_count, tweet.view_count ]
      prev_tweets_data.append(tweet_data)
      with open(FILEPATH, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(tweet_data)
    
    
    print(f'{datetime.now()} - Done! Got  {tweet_count} tweets')


    print(f'{datetime.now()} - Done! Got  {tweet_count} tweets found')


asyncio.run(main())
