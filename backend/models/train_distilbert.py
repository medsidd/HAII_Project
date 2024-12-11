import pandas as pd
from sklearn.model_selection import train_test_split
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
import os

class DistilBERTModel:
    def __init__(self, model_path="./distilbert_trained_model"):
        self.model_path = model_path
        self.tokenizer = DistilBertTokenizer.from_pretrained(model_path)
        self.model = DistilBertForSequenceClassification.from_pretrained(model_path)

    def diagnose(self, chat_history):
        """
        Analyze chat history and predict mental health conditions.

        Args:
            chat_history (list): A list of chat messages (strings).

        Returns:
            dict: A dictionary of conditions and their corresponding confidence scores.
        """
        try:
            # Tokenize chat history
            inputs = self.tokenizer(
                chat_history,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )
            
            # Run model prediction
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.softmax(logits, dim=1).mean(dim=0)  # Average probabilities across chat history
            confidence_scores = probabilities.tolist()

            # Map predictions to condition labels
            label_mapping = {
                0: "Stress",
                1: "Depression",
                2: "Bipolar Disorder",
                3: "Personality Disorder",
                4: "Anxiety"
            }
            diagnosis = {label_mapping[i]: confidence_scores[i] for i in range(len(confidence_scores))}

            return diagnosis

        except Exception as e:
            print("Error in diagnosis:", e)
            return {}



# Training Logic
def train_distilbert():
    data_path = '/Users/medsidd/mental_health_app/data/preprocessed_data.csv'
    df = pd.read_csv(data_path)

    # Map targets to their respective labels
    label_mapping = {
        0: "Stress",
        1: "Depression",
        2: "Bipolar Disorder",
        3: "Personality Disorder",
        4: "Anxiety"
    }
    df['target'] = df['target'].apply(lambda x: label_mapping[x])
    df['text'] = df['text'].astype(str)

    tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
    reverse_label_mapping = {v: k for k, v in label_mapping.items()}
    df['labels'] = df['target'].apply(lambda x: reverse_label_mapping[x])

    # Convert pandas DataFrame to Hugging Face Dataset
    dataset = Dataset.from_pandas(df)

    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=512)

    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    tokenized_dataset = tokenized_dataset.map(lambda examples: {"labels": examples["labels"]}, batched=True)

    # Train-test split
    train_dataset, val_dataset = tokenized_dataset.train_test_split(test_size=0.2).values()

    model = DistilBertForSequenceClassification.from_pretrained(
        "distilbert-base-uncased",
        num_labels=len(label_mapping),
        id2label={i: label for i, label in enumerate(label_mapping.values())},
        label2id={label: i for i, label in enumerate(label_mapping.values())}
    )

    training_args = TrainingArguments(
        output_dir="./distilbert_results",
        eval_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
        save_total_limit=1,
        logging_dir="./logs"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer
    )

    trainer.train()

    model.save_pretrained("./distilbert_trained_model", safe_serialization=False)
    tokenizer.save_pretrained("./distilbert_trained_model")


    print("Model training complete. Model saved in './distilbert_trained_model'")

# Run training only when executed directly
if __name__ == "__main__":
    train_distilbert()
