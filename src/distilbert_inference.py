"""Inference-only wrapper around the saved TerpLoad DistilBERT model."""

from pathlib import Path

import joblib
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from workload_labels import get_workload_labels


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_DIR = PROJECT_ROOT / "results" / "distilbert_model"


class SavedModelUnavailableError(RuntimeError):
    """Raised when this checkout does not contain the trained model files."""


class DistilBertWorkloadModel:
    """Load the fine-tuned model once and classify review text in batches."""

    def __init__(self, model_dir=DEFAULT_MODEL_DIR, batch_size=16, max_length=256):
        self.model_dir = Path(model_dir)
        if not (self.model_dir / "config.json").exists():
            raise SavedModelUnavailableError(
                "Saved DistilBERT model not found at "
                f"{self.model_dir}. Copy the training output directory there; "
                "the application never retrains during inference."
            )

        weights_path = self.model_dir / "model.safetensors"
        if not weights_path.exists():
            raise SavedModelUnavailableError(
                f"Saved DistilBERT weights not found at {weights_path}."
            )
        with weights_path.open("rb") as file:
            prefix = file.read(128)
        if prefix.startswith(b"version https://git-lfs.github.com/spec/v1"):
            raise SavedModelUnavailableError(
                "model.safetensors is a Git LFS pointer, not the trained model. "
                "Install Git LFS and pull the artifact before starting the app."
            )

        self.labels = get_workload_labels()
        thresholds_path = self.model_dir / "thresholds.joblib"
        if not thresholds_path.exists():
            raise SavedModelUnavailableError(
                f"Saved DistilBERT thresholds not found at {thresholds_path}."
            )
        self.thresholds = joblib.load(thresholds_path)
        self.batch_size = batch_size
        self.max_length = max_length
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_dir
        ).to(self.device)
        self.model.eval()

    def predict(self, review_texts):
        """Return one probability dictionary per input review, without training."""
        results = []
        texts = [str(text or "") for text in review_texts]
        with torch.no_grad():
            for start in range(0, len(texts), self.batch_size):
                batch = texts[start : start + self.batch_size]
                encoded = self.tokenizer(
                    batch,
                    truncation=True,
                    padding=True,
                    max_length=self.max_length,
                    return_tensors="pt",
                ).to(self.device)
                probabilities = torch.sigmoid(self.model(**encoded).logits).cpu()
                for row in probabilities.tolist():
                    results.append(dict(zip(self.labels, row)))
        return results
