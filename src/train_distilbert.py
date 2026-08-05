# train_distilbert.py
"""
DistilBERT training pipeline matching the TF-IDF evaluation protocol.

Outputs:
- results/distilbert_metrics.json
- results/distilbert_predictions.csv
- results/distilbert_thresholds.json
- results/model_comparison.csv
- results/distilbert_model/
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import torch

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    f1_score,
    hamming_loss,
)

from torch.utils.data import Dataset, DataLoader
from transformers import (
    DistilBertTokenizer,
    DistilBertForSequenceClassification,
)

TRAIN_PATH = "data/splits/train.csv"
VAL_PATH = "data/splits/val.csv"
TEST_PATH = "data/splits/test.csv"

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

LABEL_COLUMNS = [
    "project_heavy",
    "exam_heavy",
    "homework_heavy",
    "time_consuming",
]

MAX_LENGTH = 256
BATCH_SIZE = 8
EPOCHS = 3
LR = 2e-5

THRESHOLD_CANDIDATES = np.arange(0.10,0.91,0.05)

train_df = pd.read_csv(TRAIN_PATH)
val_df = pd.read_csv(VAL_PATH)
test_df = pd.read_csv(TEST_PATH)

train_texts=train_df.review_text.fillna("").astype(str).tolist()
val_texts=val_df.review_text.fillna("").astype(str).tolist()
test_texts=test_df.review_text.fillna("").astype(str).tolist()

train_labels=train_df[LABEL_COLUMNS].astype(int).values
val_labels=val_df[LABEL_COLUMNS].astype(int).values
test_labels=test_df[LABEL_COLUMNS].astype(int).values

tokenizer=DistilBertTokenizer.from_pretrained("distilbert-base-uncased")

def encode(texts):
    return tokenizer(texts,truncation=True,padding=True,max_length=MAX_LENGTH)

class ReviewDataset(Dataset):
    def __init__(self,encodings,labels):
        self.encodings=encodings
        self.labels=labels
    def __len__(self):
        return len(self.labels)
    def __getitem__(self,idx):
        item={k:torch.tensor(v[idx]) for k,v in self.encodings.items()}
        item["labels"]=torch.tensor(self.labels[idx],dtype=torch.float)
        return item

train_loader=DataLoader(ReviewDataset(encode(train_texts),train_labels),batch_size=BATCH_SIZE,shuffle=True)
val_loader=DataLoader(ReviewDataset(encode(val_texts),val_labels),batch_size=BATCH_SIZE)
test_loader=DataLoader(ReviewDataset(encode(test_texts),test_labels),batch_size=BATCH_SIZE)

device=torch.device("cuda" if torch.cuda.is_available() else "cpu")

model=DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=len(LABEL_COLUMNS),
    problem_type="multi_label_classification",
).to(device)

optimizer=torch.optim.AdamW(model.parameters(),lr=LR)

print("Training...")
model.train()
for epoch in range(EPOCHS):
    loss_sum=0
    for batch in train_loader:
        optimizer.zero_grad()
        batch={k:v.to(device) for k,v in batch.items()}
        out=model(**batch)
        out.loss.backward()
        optimizer.step()
        loss_sum+=out.loss.item()
    print(f"Epoch {epoch+1}: {loss_sum/len(train_loader):.4f}")

def predict(loader):
    model.eval()
    probs=[]
    truths=[]
    with torch.no_grad():
        for batch in loader:
            truths.extend(batch["labels"].numpy())
            gpu={
                "input_ids":batch["input_ids"].to(device),
                "attention_mask":batch["attention_mask"].to(device)
            }
            logits=model(**gpu).logits
            probs.extend(torch.sigmoid(logits).cpu().numpy())
    return np.array(probs),np.array(truths)

val_probs,val_truths=predict(val_loader)
test_probs,test_truths=predict(test_loader)

thresholds={}
test_preds=np.zeros_like(test_truths)

metrics={}
for i,label in enumerate(LABEL_COLUMNS):
    best_t=0.5
    best_f1=-1
    for t in THRESHOLD_CANDIDATES:
        preds=(val_probs[:,i]>=t).astype(int)
        _,_,f1,_=precision_recall_fscore_support(
            val_truths[:,i],preds,
            average="binary",
            zero_division=0
        )
        if f1>best_f1:
            best_f1=f1
            best_t=float(round(t,2))
    thresholds[label]=best_t
    preds=(test_probs[:,i]>=best_t).astype(int)
    test_preds[:,i]=preds
    p,r,f1,_=precision_recall_fscore_support(
        test_truths[:,i],preds,
        average="binary",
        zero_division=0
    )
    metrics[label]={
        "selected_threshold":best_t,
        "test":{
            "accuracy":float(accuracy_score(test_truths[:,i],preds)),
            "precision":float(p),
            "recall":float(r),
            "f1":float(f1),
            "support":int(test_truths[:,i].sum()),
            "total":int(len(test_truths))
        }
    }

metrics["overall_test"]={
    "macro_f1":float(f1_score(test_truths,test_preds,average="macro",zero_division=0)),
    "micro_f1":float(f1_score(test_truths,test_preds,average="micro",zero_division=0)),
    "subset_accuracy":float(accuracy_score(test_truths,test_preds)),
    "hamming_loss":float(hamming_loss(test_truths,test_preds)),
    "test_rows":int(len(test_df))
}

pred_df=test_df[["review_text"]].copy()
for i,label in enumerate(LABEL_COLUMNS):
    pred_df[f"{label}_true"]=test_truths[:,i]
    pred_df[f"{label}_probability"]=test_probs[:,i]
    pred_df[f"{label}_pred"]=test_preds[:,i]

pred_df.to_csv(os.path.join(RESULTS_DIR,"distilbert_predictions.csv"),index=False)

with open(os.path.join(RESULTS_DIR,"distilbert_metrics.json"),"w") as f:
    json.dump(metrics,f,indent=4)

with open(os.path.join(RESULTS_DIR,"distilbert_thresholds.json"),"w") as f:
    json.dump(thresholds,f,indent=4)

model_dir=os.path.join(RESULTS_DIR,"distilbert_model")
model.save_pretrained(model_dir)
tokenizer.save_pretrained(model_dir)
joblib.dump(thresholds,os.path.join(model_dir,"thresholds.joblib"))
joblib.dump(LABEL_COLUMNS,os.path.join(model_dir,"labels.joblib"))

def load(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}

tfidf=load(os.path.join(RESULTS_DIR,"tfidf_metrics.json"))
distil=metrics

comparison=pd.DataFrame([
    {
        "Model":"TF-IDF",
        "Subset Accuracy":tfidf.get("overall_test",{}).get("subset_accuracy"),
        "Macro F1":tfidf.get("overall_test",{}).get("macro_f1"),
        "Micro F1":tfidf.get("overall_test",{}).get("micro_f1"),
        "Hamming Loss":tfidf.get("overall_test",{}).get("hamming_loss"),
    },
    {
        "Model":"DistilBERT",
        "Subset Accuracy":distil["overall_test"]["subset_accuracy"],
        "Macro F1":distil["overall_test"]["macro_f1"],
        "Micro F1":distil["overall_test"]["micro_f1"],
        "Hamming Loss":distil["overall_test"]["hamming_loss"],
    }
])

comparison.to_csv(os.path.join(RESULTS_DIR,"model_comparison.csv"),index=False)

print("Finished.")