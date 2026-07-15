import pandas as pd
import torch

from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader

from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
)

CSV_PATH = "data/labeled_reviews_sample.csv"

LABEL_COLUMNS = [
    "project_heavy",
    "exam_heavy",
    "homework_heavy",
    "time_consuming",
]

MAX_LENGTH = 256
BATCH_SIZE = 8

df = pd.read_csv(CSV_PATH)

print("Dataset shape:", df.shape)

texts = df["review_text"].astype(str).tolist()
labels = df[LABEL_COLUMNS].values

print("Number of reviews:", len(texts))
print("Label shape:", labels.shape)


train_texts, val_texts, train_labels, val_labels = train_test_split(
    texts,
    labels,
    test_size=0.2,
    random_state=42,
)

print("Training samples:", len(train_texts))
print("Validation samples:", len(val_texts))


tokenizer = DistilBertTokenizer.from_pretrained(
    "distilbert-base-uncased"
)

train_encodings = tokenizer(
    train_texts,
    truncation=True,
    padding=True,
    max_length=MAX_LENGTH,
)

val_encodings = tokenizer(
    val_texts,
    truncation=True,
    padding=True,
    max_length=MAX_LENGTH,
)

print("Tokenization complete.")


class ReviewDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {
            key: torch.tensor(val[idx])
            for key, val in self.encodings.items()
        }

        item["labels"] = torch.tensor(
            self.labels[idx],
            dtype=torch.float,
        )

        return item


train_dataset = ReviewDataset(
    train_encodings,
    train_labels,
)

val_dataset = ReviewDataset(
    val_encodings,
    val_labels,
)


train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
)

print("DataLoaders created.")


model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=4,
    problem_type="multi_label_classification",
)

print("Model loaded.")


batch = next(iter(train_loader))

outputs = model(
    input_ids=batch["input_ids"],
    attention_mask=batch["attention_mask"],
    labels=batch["labels"],
)

print("\nForward pass successful!")

print("Loss:")
print(outputs.loss.item())

print("\nLogits shape:")
print(outputs.logits.shape)

print("\nExpected:")
print(f"({BATCH_SIZE}, 4)")

print("\nExample logits:")
print(outputs.logits[0])

print("\nDone!")