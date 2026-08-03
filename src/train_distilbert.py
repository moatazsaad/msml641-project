import os
import json
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from torch.utils.data import Dataset, DataLoader
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

TRAIN_PATH = "data/splits/train.csv"
VAL_PATH = "data/splits/val.csv"
TEST_PATH = "data/splits/test.csv"


LABEL_COLUMNS = [
    "project_heavy",
    "exam_heavy",
    "homework_heavy",
    "time_consuming",
]

train_df = pd.read_csv(TRAIN_PATH)
val_df = pd.read_csv(VAL_PATH)
test_df = pd.read_csv(TEST_PATH)

train_texts = train_df["review_text"].astype(str).tolist()
val_texts = val_df["review_text"].astype(str).tolist()
test_texts = test_df["review_text"].astype(str).tolist()

train_labels = train_df[LABEL_COLUMNS].astype(int).values
val_labels = val_df[LABEL_COLUMNS].astype(int).values
test_labels = test_df[LABEL_COLUMNS].astype(int).values

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

MAX_LENGTH = 256
BATCH_SIZE = 8
EPOCHS = 3
LR = 2e-5



tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")

train_encodings = tokenizer(
    train_texts,
    truncation=True,
    padding=True,
    max_length=MAX_LENGTH,
)

test_encodings = tokenizer(
    test_texts,
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

class ReviewDataset(Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = {k: torch.tensor(v[idx]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[idx], dtype=torch.float)
        return item

train_loader = DataLoader(
    ReviewDataset(train_encodings, train_labels),
    batch_size=BATCH_SIZE,
    shuffle=True,
)

test_loader = DataLoader(
    ReviewDataset(test_encodings, test_labels),
    batch_size=BATCH_SIZE,
)
val_loader = DataLoader(
    ReviewDataset(val_encodings, val_labels),
    batch_size=BATCH_SIZE,
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=4,
    problem_type="multi_label_classification",
).to(device)

optimizer = torch.optim.AdamW(model.parameters(), lr=LR)

print("Training...")

model.train()

for epoch in range(EPOCHS):
    total_loss = 0.0
    for batch in train_loader:
        optimizer.zero_grad()

        batch = {k: v.to(device) for k, v in batch.items()}

        outputs = model(**batch)
        loss = outputs.loss

        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch+1}: loss={total_loss/len(train_loader):.4f}")

print("Evaluating...")

model.eval()

predictions = []
truths = []
texts_out = []

with torch.no_grad():
    idx = 0
    for batch in test_loader:
        labels_batch = batch["labels"]

        batch_gpu = {
            "input_ids": batch["input_ids"].to(device),
            "attention_mask": batch["attention_mask"].to(device),
        }

        outputs = model(**batch_gpu)

        probs = torch.sigmoid(outputs.logits).cpu().numpy()
        preds = (probs >= 0.5).astype(int)

        predictions.extend(preds)
        truths.extend(labels_batch.numpy())

        bs = len(preds)
        texts_out.extend(test_texts[idx:idx+bs])
        idx += bs

predictions = np.array(predictions)
truths = np.array(truths)

pred_df = pd.DataFrame({"review_text": texts_out})

for i, label in enumerate(LABEL_COLUMNS):
    pred_df[f"{label}_true"] = truths[:, i]
    pred_df[f"{label}_pred"] = predictions[:, i]

pred_df.to_csv(
    os.path.join(RESULTS_DIR, "distilbert_predictions.csv"),
    index=False,
)

metrics = {}

macro_f1 = []

for i, label in enumerate(LABEL_COLUMNS):
    p, r, f1, _ = precision_recall_fscore_support(
        truths[:, i],
        predictions[:, i],
        average="binary",
        zero_division=0,
    )

    metrics[label] = {
        "precision": float(p),
        "recall": float(r),
        "f1": float(f1),
    }

    macro_f1.append(f1)

subset_accuracy = accuracy_score(truths, predictions)

metrics["accuracy"] = float(subset_accuracy)
metrics["macro_f1"] = float(np.mean(macro_f1))

with open(os.path.join(RESULTS_DIR, "distilbert_metrics.json"), "w") as f:
    json.dump(metrics, f, indent=4)

def load_metrics(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"accuracy": None, "macro_f1": None}

keyword = load_metrics(os.path.join(RESULTS_DIR, "keyword_baseline_metrics.json"))
tfidf = load_metrics(os.path.join(RESULTS_DIR, "tfidf_metrics.json"))
distil = load_metrics(os.path.join(RESULTS_DIR, "distilbert_metrics.json"))

comparison = pd.DataFrame([
    {
        "Model": "Keyword",
        "Accuracy": keyword.get("accuracy"),
        "Macro F1": keyword.get("macro_f1"),
    },
    {
        "Model": "TF-IDF",
        "Accuracy": tfidf.get("accuracy"),
        "Macro F1": tfidf.get("macro_f1"),
    },
    {
        "Model": "DistilBERT",
        "Accuracy": distil.get("accuracy"),
        "Macro F1": distil.get("macro_f1"),
    },
])

comparison.to_csv(
    os.path.join(RESULTS_DIR, "model_comparison.csv"),
    index=False,
)

print("Finished.")
