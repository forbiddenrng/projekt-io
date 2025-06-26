import pandas as pd
import os

def load_tweets(filepath):
  try:
    tweets_df = pd.read_csv(filepath)
    return tweets_df
  except Exception as e:
    print(f"Error while loading file {filepath}: {e}")
    return None      


def load_all_tweets(file_paths=None):

  if file_paths is None:
    return None
  
  exclude_files = ["top_po.csv", "top_przed.csv"]
  dataframes = []
  for path in file_paths:
    filename = os.path.basename(path)

    if filename in exclude_files:
      continue
    
    df = load_tweets(path)
    if df is not None:
      dataframes.append(df)
  
  if dataframes:
    combinded_df = pd.concat(dataframes, ignore_index=True)
    return combinded_df
  else:
    print("No valid data files were loaded")
    return None
