import os
import pandas as pd
import matplotlib.pyplot as plt
import glob

# Base directory
base_dir = "c:/Users/antek/Desktop/projekt_io"

# Paths for Nawrocki tweets
nawrocki_mieszkanie_dir = os.path.join(base_dir, "momenty_nawrocki/mieszkanie")
nawrocki_snus_dir = os.path.join(base_dir, "momenty_nawrocki/snus")

# Paths for Trzaskowski tweets
trzaskowski_debata_dir = os.path.join(base_dir, "momenty_trzaskowski/debata")
trzaskowski_nask_dir = os.path.join(base_dir, "momenty_trzaskowski/nask")
trzaskowski_obietnica_dir = os.path.join(base_dir, "momenty_trzaskowski/obietnica")
trzaskowski_csv_files = [
    os.path.join(base_dir, "momenty_trzaskowski/account_trzaskowski.csv"),
    os.path.join(base_dir, "momenty_trzaskowski/latest_trzaskowski.csv"),
    os.path.join(base_dir, "momenty_trzaskowski/trzaskowski1.csv"),
    os.path.join(base_dir, "momenty_trzaskowski/trzaskowski2.csv")
]

# Function to read all CSV files from a folder
def read_csv_files_from_dir(folder_path):
    all_data = pd.DataFrame()
    for csv_file in glob.glob(os.path.join(folder_path, "*.csv")):
        try:
            df = pd.read_csv(csv_file)
            all_data = pd.concat([all_data, df])
        except Exception as e:
            print(f"Error reading {csv_file}: {e}")
    return all_data

# Function to read individual CSV files
def read_csv_file(file_path):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame()

# Read all Nawrocki tweets
print("Reading Nawrocki tweets...")
nawrocki_mieszkanie = read_csv_files_from_dir(nawrocki_mieszkanie_dir)
nawrocki_snus = read_csv_files_from_dir(nawrocki_snus_dir)
nawrocki_tweets = pd.concat([nawrocki_mieszkanie, nawrocki_snus])

# Read all Trzaskowski tweets
print("Reading Trzaskowski tweets from directories...")
trzaskowski_debata = read_csv_files_from_dir(trzaskowski_debata_dir)
trzaskowski_nask = read_csv_files_from_dir(trzaskowski_nask_dir)
trzaskowski_obietnica = read_csv_files_from_dir(trzaskowski_obietnica_dir)

print("Reading Trzaskowski individual CSV files...")
trzaskowski_individual_files = pd.DataFrame()
for file_path in trzaskowski_csv_files:
    try:
        df = read_csv_file(file_path)
        trzaskowski_individual_files = pd.concat([trzaskowski_individual_files, df])
    except:
        print(f"Could not read {file_path}")

trzaskowski_tweets = pd.concat([
    trzaskowski_debata, 
    trzaskowski_nask, 
    trzaskowski_obietnica, 
    trzaskowski_individual_files
])

# Count tweets
nawrocki_count = len(nawrocki_tweets)
trzaskowski_count = len(trzaskowski_tweets)
total_count = nawrocki_count + trzaskowski_count

# Print results
print(f"Total tweets about Karol Nawrocki: {nawrocki_count}")
print(f"Total tweets about Rafał Trzaskowski: {trzaskowski_count}")
print(f"Total tweets overall: {total_count}")

# Create a simple bar chart
candidates = ['Karol Nawrocki', 'Rafał Trzaskowski', 'Total']
counts = [nawrocki_count, trzaskowski_count, total_count]

plt.figure(figsize=(10, 6))
bars = plt.bar(candidates, counts, color=['blue', 'orange', 'gray'])

# Add count labels on top of each bar
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
             f'{height:,}', ha='center', va='bottom', fontsize=12)

plt.title('Number of Tweets by Candidate', fontsize=16, fontweight='bold')
plt.ylabel('Number of Tweets', fontsize=14)
plt.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('candidate_tweet_counts.png', dpi=300)
plt.show()