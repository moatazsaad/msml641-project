import json
from pathlib import Path
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score

LABELS=["project_heavy","exam_heavy","homework_heavy","time_consuming"]

# With this few labeled reviews, a single train/test split leaves too few
# test examples (and even fewer positive ones for the rare labels) to trust.
# 5-fold cross-validation instead predicts every review exactly once, using a
# model that never saw it during training, so metrics use every labeled review.
N_FOLDS = 5

def main():
    # week08 = original 64 labeled reviews, week10 = 40 more labeled the same way.
    # Same columns, no overlapping review_id values, so a plain concat is safe.
    df=pd.concat(
        [pd.read_csv("data/weakly-labeled-week08.csv"), pd.read_csv("data/weakly-labeled-week10.csv")],
        ignore_index=True,
    )
    results=Path("results"); results.mkdir(exist_ok=True)
    metrics={}
    texts=df["review_text"].fillna("")
    pred_df=pd.DataFrame({"review_text":texts})
    for label in LABELS:
        y=df[label].astype(int)
        pipe=Pipeline([("tfidf",TfidfVectorizer(stop_words="english")),("clf",LogisticRegression(max_iter=1000,class_weight="balanced"))])
        cv=StratifiedKFold(n_splits=N_FOLDS,shuffle=True,random_state=42)
        # out-of-fold predictions: every review predicted once, by a model
        # that was not trained on it
        cv_pred=cross_val_predict(pipe,texts,y,cv=cv)
        pipe.fit(texts,y)
        full_pred=pipe.predict(texts)
        pred_df[label+"_true"]=y
        pred_df[label+"_pred"]=full_pred
        pred_df[label+"_cv_pred"]=cv_pred
        metrics[label]={
            "cv_folds":N_FOLDS,
            "accuracy":accuracy_score(y,cv_pred),
            "precision":precision_score(y,cv_pred,zero_division=0),
            "recall":recall_score(y,cv_pred,zero_division=0),
            "f1":f1_score(y,cv_pred,zero_division=0)
        }
    pred_df.to_csv(results/"tfidf_predictions.csv",index=False)
    with open(results/"tfidf_metrics.json","w") as f:
        json.dump(metrics,f,indent=4)
    print(json.dumps(metrics,indent=2))
if __name__=="__main__":
    main()

