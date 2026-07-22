import json
from pathlib import Path
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score

LABELS=["project_heavy","exam_heavy","homework_heavy","time_consuming"]

def main():
    df=pd.read_csv("data\weakly-labeled-week08.csv")
    results=Path("results"); results.mkdir(exist_ok=True)
    metrics={}
    pred_df=pd.DataFrame({"review_text":df["review_text"]})
    for label in LABELS:
        X_train,X_test,y_train,y_test=train_test_split(df["review_text"].fillna(""),df[label].astype(int),test_size=0.2,random_state=42,stratify=df[label])
        pipe=Pipeline([("tfidf",TfidfVectorizer(stop_words="english")),("clf",LogisticRegression(max_iter=1000))])
        pipe.fit(X_train,y_train)
        full_pred=pipe.predict(df["review_text"].fillna(""))
        pred_df[label+"_true"]=df[label].astype(int)
        pred_df[label+"_pred"]=full_pred
        test_pred=pipe.predict(X_test)
        metrics[label]={
            "accuracy":accuracy_score(y_test,test_pred),
            "precision":precision_score(y_test,test_pred,zero_division=0),
            "recall":recall_score(y_test,test_pred,zero_division=0),
            "f1":f1_score(y_test,test_pred,zero_division=0)
        }
    pred_df.to_csv(results/"tfidf_predictions.csv",index=False)
    with open(results/"tfidf_metrics.json","w") as f:
        json.dump(metrics,f,indent=4)
    print(json.dumps(metrics,indent=2))
if __name__=="__main__":
    main()

