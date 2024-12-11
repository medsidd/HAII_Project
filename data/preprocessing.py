import pandas as pd
import re
import os

# Load the dataset
file_path = '/Users/medsidd/mental_health_app/data/mental_health_dataset.csv'
dataset = pd.read_csv(file_path)

# Drop unnecessary columns
dataset = dataset.drop(columns=['Unnamed: 0', 'title'], errors='ignore')

# Remove missing values
dataset = dataset.dropna(subset=['text', 'target'])

# Remove duplicate rows based on the 'text' column
dataset = dataset.drop_duplicates(subset='text')

# Clean text data
def clean_text(text):
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Convert to lowercase
    text = text.lower()
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

dataset['text'] = dataset['text'].apply(clean_text)

# Save the preprocessed dataset
output_dir = '/Users/medsidd/mental_health_app/data'
output_file = os.path.join(output_dir, 'preprocessed_data.csv')
dataset.to_csv(output_file, index=False)

print(f"Preprocessed data saved to {output_file}")
