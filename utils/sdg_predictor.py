import os

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# SciBERT fine-tuned for SDG classification (https://huggingface.co/dvdblk/scibert_sdg_cased_zo-up)
MODEL_NAME = "dvdblk/scibert_sdg_cased_zo-up"
MODEL_DIR = "./data/pipeline/model/scibert_sdg_classification"
MAX_LEN = 512

_tokenizer = None
_model = None


def _load_model():
    """Load the model once. Download it from Hugging Face on first use and keep a local copy."""
    global _tokenizer, _model
    if _model is not None:
        return _tokenizer, _model

    if not os.path.isdir(MODEL_DIR):
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        tokenizer.save_pretrained(MODEL_DIR)
        model.save_pretrained(MODEL_DIR)

    _tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
    _model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
    _model.eval()
    return _tokenizer, _model


def sdg_predictor(abstract: str):
    """Return a tensor of shape (1, 17) with one probability per SDG."""
    tokenizer, model = _load_model()

    # Truncate to the model's maximum input length (512 tokens)
    inputs = tokenizer(
        abstract,
        padding=True,
        truncation=True,
        max_length=MAX_LEN,
        return_tensors="pt",
    )

    with torch.no_grad():
        logits = model(**inputs).logits

    # Multi-label model: one independent probability per SDG
    return torch.sigmoid(logits)
