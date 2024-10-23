import argparse
import glob
import logging
import os

import pandas as pd
import tensorflow as tf
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from tensorflow.keras.mixed_precision import set_global_policy
from tqdm import tqdm
from transformers import BertTokenizer, TFBertModel

# set_global_policy('mixed_float16') # Reduce RAM, only viable for GPUs
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # avoid cuda warnings

# Limit TensorFlow to a fraction of the system's available memory
gpus = tf.config.experimental.list_physical_devices("GPU")
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_virtual_device_configuration(
                gpu,
                [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=2048)],
            )  # Limit to 4GB
    except RuntimeError as e:
        print(e)

# Setup Logging
logging.basicConfig(
    filename="data/pipeline/aurora/logs/fine_tuning.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Initialize the logger
logger = logging.getLogger(__name__)


def log_model_details(model):
    """
    Log the details of the model including its summary, layers, and weights.

    Args:
        model (tf.keras.Model): The model to be logged.
    """
    # Log model summary
    model_summary = []
    model.summary(print_fn=lambda x: model_summary.append(x))
    logger.info("Model Summary:\n" + "\n".join(model_summary))

    # Log each layer's details
    for layer in model.layers:
        logger.info(f"Layer Name: {layer.name}")
        logger.info(f"Layer Type: {type(layer)}")
        logger.info(f"Layer Output Shape: {layer.output_shape}")

        # Log layer weights
        weights = layer.get_weights()
        if weights:
            logger.info(f"Layer Weights: {[w.shape for w in weights]}")
        else:
            logger.info("Layer has no weights.")


# Define the fine-tuning class
class FineTuneSDGModel:
    def __init__(
        self,
        model_path,
        sdg_label="SDG01",
        tokenizer_name="bert-base-multilingual-uncased",
    ):
        """
        Initialize the fine-tuning class.

        Args:
            model_path (str): Path to the pre-trained Keras model (.h5 file).
            sdg_label (str): The SDG label to use for evaluation (e.g., "SDG01").
            tokenizer_name (str): Name of the tokenizer to use for text processing.
        """
        self.model_path = model_path
        self.sdg_label = sdg_label
        self.tokenizer = BertTokenizer.from_pretrained(tokenizer_name)
        self.model = self._load_model()

    def _load_model(self):
        """
        Load the Keras model from the given path.

        Returns:
            model (tf.keras.Model): Loaded Keras model.
        """
        try:
            # Use custom_object_scope to register the custom layers
            with tf.keras.utils.custom_object_scope({"TFBertMainLayer": TFBertModel}):
                model = tf.keras.models.load_model(self.model_path)
            logger.info(f"Model loaded successfully from {self.model_path}")

            # Log model details
            log_model_details(model)
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
        return model

    def preprocess_texts(self, texts):
        """
        Preprocess input texts using the tokenizer.

        Args:
            texts (list of str): List of input texts to be tokenized.

        Returns:
            input_ids (tf.Tensor): Tokenized input IDs.
            attention_masks (tf.Tensor): Attention masks for the input texts.
        """
        input_ids = []
        attention_masks = []

        for text in tqdm(texts, desc="Tokenizing Texts"):
            encoding = self.tokenizer(
                text,
                return_tensors="tf",
                padding="max_length",
                truncation=True,
                max_length=512,
                return_attention_mask=True,
            )
            # Replace tokens not in the vocab with the [UNK] token
            input_ids_tensor = encoding["input_ids"]
            input_ids_tensor = tf.where(
                input_ids_tensor >= self.tokenizer.vocab_size,
                self.tokenizer.unk_token_id,
                input_ids_tensor,
            )

            input_ids.append(input_ids_tensor)
            attention_masks.append(encoding["attention_mask"])

        # Rename 'attention_mask' to 'attention_masks' to match model's input
        return tf.concat(input_ids, axis=0), tf.concat(attention_masks, axis=0)

    def compile_model(self):
        """
        Compile the model with the specified loss function, optimizer, and metrics.
        """
        self.model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
            loss=tf.keras.losses.BinaryCrossentropy(
                from_logits=False
            ),  # Set from_logits to False
            metrics=[tf.keras.metrics.BinaryAccuracy()],
        )
        logger.info("Model compiled with Adam optimizer and binary cross-entropy loss.")

    def fine_tune(self, texts, labels, epochs=3, batch_size=8):
        """
        Fine-tune the model using the provided texts and labels.

        Args:
            texts (list of str): List of input texts for training.
            labels (list of int): Corresponding labels for the input texts.
            epochs (int): Number of epochs for fine-tuning.
            batch_size (int): Batch size for training.
        """
        # Preprocess the texts
        logger.info("Starting text preprocessing...")
        input_ids, attention_masks = self.preprocess_texts(texts)
        labels_tensor = tf.convert_to_tensor(labels, dtype=tf.float32)

        # Create a TensorFlow dataset
        train_dataset = tf.data.Dataset.from_tensor_slices(
            (
                {"input_ids": input_ids, "attention_masks": attention_masks},
                labels_tensor,
            )
        )
        train_dataset = train_dataset.shuffle(buffer_size=1024).batch(batch_size)

        # Compile the model
        self.compile_model()

        # Fine-tune the model
        logger.info("Starting fine-tuning...")
        self.model.fit(train_dataset, epochs=epochs, verbose=1)
        logger.info(f"Fine-tuning completed for {epochs} epochs.")

    def save_model(self, save_path):
        """
        Save the fine-tuned model to the specified path.

        Args:
            save_path (str): Path to save the fine-tuned model.
        """
        try:
            self.model.save(save_path)
            logger.info(f"Model saved successfully to {save_path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            raise

    def load_evaluation_data(self, csv_path):
        """
        Load evaluation data from a CSV file for the specific SDG.

        Args:
            csv_path (str): Path to the CSV file containing evaluation data.

        Returns:
            tuple: A tuple containing a list of texts and a list of binary targets for the specific SDG.
        """
        df = pd.read_csv(csv_path)

        # Extract texts (abstracts) and the specific SDG column
        texts = df["abstract_cleaned"].fillna("").tolist()
        labels = (
            df[self.sdg_label].fillna(0).astype(int).tolist()
        )  # Extract specific SDG column

        return texts, labels

    def evaluate(self, texts, labels):
        """
        Evaluate the model using the given texts and binary targets for a specific SDG.

        Args:
            texts (list of str): List of input texts for evaluation.
            labels (list of int): Corresponding binary targets (0 or 1) for the specific SDG.

        Returns:
            dict: A dictionary containing evaluation metrics.
        """
        # Preprocess the texts
        input_ids, attention_masks = self.preprocess_texts(texts)

        # Create a TensorFlow dataset for evaluation
        eval_dataset = tf.data.Dataset.from_tensor_slices(
            {"input_ids": input_ids, "attention_masks": attention_masks}
        ).batch(
            8
        )  # Use a batch size for efficient evaluation

        # Get model predictions
        predictions = self.model.predict(eval_dataset)

        # Since the output is binary, apply a threshold (e.g., 0.5) to classify
        predicted_labels = (predictions > 0.5).astype(int).flatten()

        # Calculate metrics for binary classification
        accuracy = accuracy_score(labels, predicted_labels)
        precision = precision_score(labels, predicted_labels)
        recall = recall_score(labels, predicted_labels)
        f1 = f1_score(labels, predicted_labels)

        # Log and return the metrics
        logger.info(f"Accuracy: {accuracy}")
        logger.info(f"Precision: {precision}")
        logger.info(f"Recall: {recall}")
        logger.info(f"F1 Score: {f1}")

        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
        }


def load_texts_and_labels(data_dir):
    texts = []
    labels = []

    for file_path in glob.glob(os.path.join(data_dir, "*.txt")):
        with open(file_path, "r", encoding="utf-8") as file:
            texts.append(file.read())
        # Extract label from the filename (e.g., "1_text1.txt" -> label = 1)
        label = int(os.path.basename(file_path).split("_")[0])
        labels.append(label)

    return texts, labels


def main(args):
    fine_tuner = FineTuneSDGModel(model_path=args.model_path, sdg_label=args.sdg_label)

    # Load training data
    texts, labels = load_texts_and_labels(args.data_dir)

    # Load evaluation data
    eval_texts, eval_labels = fine_tuner.load_evaluation_data(args.eval_csv)

    # Evaluate the model before fine-tuning
    logger.info("Evaluating model before fine-tuning...")
    initial_metrics = fine_tuner.evaluate(eval_texts, eval_labels)
    logger.info(f"Initial Metrics: {initial_metrics}")

    # Fine-tune the model
    fine_tuner.fine_tune(texts, labels, epochs=args.epochs, batch_size=args.batch_size)

    # Save the fine-tuned model
    fine_tuner.save_model(args.save_path)

    # Evaluate the model after fine-tuning
    logger.info("Evaluating model after fine-tuning...")
    final_metrics = fine_tuner.evaluate(eval_texts, eval_labels)
    logger.info(f"Final Metrics: {final_metrics}")

    # Log performance improvement
    logger.info(
        f"Performance Improvement (F1 Score): {final_metrics['f1_score'] - initial_metrics['f1_score']}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine-tune an SDG model.")
    parser.add_argument(
        "--model_path",
        type=str,
        required=True,
        help="Path to the pre-trained model (.h5 file).",
    )
    parser.add_argument(
        "--data_dir",
        type=str,
        required=True,
        help="Directory containing input text files.",
    )
    parser.add_argument(
        "--epochs", type=int, default=3, help="Number of epochs for fine-tuning."
    )
    parser.add_argument(
        "--batch_size", type=int, default=8, help="Batch size for fine-tuning."
    )
    parser.add_argument(
        "--eval_csv",
        type=str,
        required=True,
        help="Path to the evaluation CSV file.",
    )
    parser.add_argument(
        "--sdg_label",
        type=str,
        required=True,
        help="The SDG label to use for evaluation (e.g., 'SDG01').",
    )
    parser.add_argument(
        "--save_path",
        type=str,
        required=True,
        help="Path to save the fine-tuned model.",
    )

    args = parser.parse_args()
    main(args)


# python -m pipeline.aurora.fine_tune --model_path "data/pipeline/aurora/models/sdg1.h5" --data_dir "data/pipeline/aurora/texts/" --epochs 1 --batch_size 2 --save_path "data/pipeline/aurora/models/fine_tuned_sdg1_model.h5"
# python -m pipeline.aurora.fine_tune --model_path "data/pipeline/aurora/models/sdg1.h5" --data_dir "data/pipeline/aurora/texts/" --eval_csv "data/pipeline/aurora/evaluation/SAMPLE_aurora_sdg_v5_worldwide_set_doi_abstracts_sdg_targets_2009-2020-in-columns.csv" --sdg_label "SDG01" --epochs 1 --batch_size 2 --save_path "data/pipeline/aurora/models/fine_tuned_sdg1_model.h5"
