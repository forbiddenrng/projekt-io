import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_trzaskowski_emotions(csv_file):
    # Load the CSV data
    df = pd.read_csv(csv_file)
    
    # Convert datetime to proper format
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Create a large figure
    plt.figure(figsize=(15, 8))
    
    # Plot each emotion with appropriate colors
    plt.plot(df['datetime'], df['Happy'], 'g-', linewidth=2, label='Happy')
    plt.plot(df['datetime'], df['Sad'], 'b-', linewidth=2, label='Sad')
    plt.plot(df['datetime'], df['Angry'], 'r-', linewidth=2, label='Angry')
    plt.plot(df['datetime'], df['Fear'], 'k-', linewidth=2, label='Fear')
    plt.plot(df['datetime'], df['Surprise'], 'y-', linewidth=2, label='Surprise')
    
    # Add tweet count as area plot
    plt.fill_between(df['datetime'], 0, 
                    df['tweet_count'] / df['tweet_count'].max() * 0.2,
                    alpha=0.2, color='gray', label='Tweet Volume (scaled)')
    
    # Add the debate event
    debate_date = pd.to_datetime("2025-04-11")
    plt.axvline(x=debate_date, color="blue", linestyle='--', alpha=0.7)
    plt.text(debate_date, 0.9, "Debata (11.04.2025)", rotation=90, 
             verticalalignment='top', fontsize=10)
    
    # Set y-axis from 0 to 1
    plt.ylim(0, 0.35)
    
    # Set labels and styling
    plt.xlabel('Date')
    plt.ylabel('Emotion Score')
    plt.title('Emotion Analysis of Tweets about Trzaskowski Debata Event')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Save the figure
    plt.tight_layout()
    output_path = 'trzaskowski_emotions_full_scale.png'
    plt.savefig(output_path)
    plt.show()
    
    print(f"Plot saved to: {output_path}")

# Path to your CSV file
csv_file = 'c:/Users/antek/Desktop/projekt_io/emotion_analysis/text2emotions/text2emotion_specific_events/trzaskowski_debata_emotions.csv'

# Create the plot
plot_trzaskowski_emotions(csv_file)