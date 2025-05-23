import math
from sqlalchemy.orm import sessionmaker
from db.mariadb_connector import engine as mariadb_engine
from models.sdg_prediction import SDGPrediction

# Initialize session
Session = sessionmaker(bind=mariadb_engine)

def calculate_entropy(values):
    """
    Calculate entropy given a list of probability values.
    """
    entropy_value = -sum(p * math.log2(p) if p != 0 else 0 for p in values)
    return round(entropy_value, 4)

def calculate_std(values):
    """
    Calculate standard deviation given a list of values.
    """
    if len(values) == 0:
        return 0.0

    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    std_deviation = math.sqrt(variance)
    return round(std_deviation, 4)

def load_and_update_predictions(batch_size=100):
    with Session() as session:
        query = session.query(SDGPrediction).filter(
            SDGPrediction.predicted.is_(True)
        )
        predictions_count = query.count()

        batch_count = (predictions_count // batch_size) + 1

        for batch_index in range(batch_count):
            offset = batch_index * batch_size
            predictions_batch = query.offset(offset).limit(batch_size).all()

            for prediction in predictions_batch:
                # Calculate SDG probabilities
                sdg_probabilities = [getattr(prediction, f"sdg{i}") for i in range(1, 18)]
                sdg_probabilities = [p for p in sdg_probabilities if p is not None]

                # Calculate entropy and std
                entropy = calculate_entropy(sdg_probabilities)
                std = calculate_std(sdg_probabilities)

                # Update prediction object
                prediction.entropy = entropy
                prediction.std = std

            # Commit batch updates
            session.commit()
            print(f"Committed batch {batch_index + 1} of {batch_count}")

if __name__ == "__main__":
    load_and_update_predictions(batch_size=500)
