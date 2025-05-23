import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

# Initially download
tokenizer = AutoTokenizer.from_pretrained("dvdblk/scibert_sdg_cased_zo-up")
model = AutoModelForSequenceClassification.from_pretrained("dvdblk/scibert_sdg_cased_zo-up")

# Store the tokenizer and model locally
tokenizer.save_pretrained("./data/pipeline/model/scibert_sdg_classification")
model.save_pretrained("./data/pipeline/model/scibert_sdg_classification")

MAX_LEN = 512

def sdg_predictor(abstract: str):
    # Load the locally stored tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained("./data/pipeline/model/scibert_sdg_classification")
    model = AutoModelForSequenceClassification.from_pretrained("./data/pipeline/model/scibert_sdg_classification")

    # Tokenize the abstract with truncation to the model's max length (512 tokens)
    inputs = tokenizer(
        abstract,
        padding=True,
        truncation=True,  # Ensure truncation if the abstract exceeds max length
        max_length=MAX_LEN,  # Define max length for tokenization
        return_tensors="pt"
    )

    # Pass the tokenized input to the model
    outputs = model(**inputs)

    # Get the predicted logits (model outputs before applying sigmoid)
    logits = outputs.logits

    # Softmax to get the predicted probabilities
    probabilities = torch.sigmoid(logits)

    # Get the predicted label (SDG class)
    predicted_class = torch.argmax(probabilities, dim=-1)

    # Results
    # print(f"Predicted probabilities: {probabilities}")
    # print(f"Predicted SDG class: {predicted_class.item() + 1}")
    return probabilities
