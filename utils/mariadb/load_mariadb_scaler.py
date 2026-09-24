from sqlalchemy.orm import sessionmaker

# Establish MariaDB connection
from db.mariadb_connector import engine as mariadb_engine
from models import Base, SDGPrediction

# Model whose predictions drive maps, levels and quests (settings: PREDICTION_MODEL, default "Aurora")
from settings.settings import MariaDBSettings as _PredictionModelSettings

PREDICTION_MODEL = _PredictionModelSettings.DEFAULT_PREDICTION_MODEL

Session = sessionmaker(bind=mariadb_engine)
session = Session()


def scale_sdg_values(sdg_value):
    """
    Linearly scale SDG values based on the given ranges:
    [0.85 - 1.00] -> [0.5 - 1.0]
    [0.00 - 0.85) -> [0.0 - 0.5)
    """
    if 0.85 <= sdg_value <= 1.00:
        return 0.5 + ((sdg_value - 0.85) / 0.15) * 0.5
    elif 0.00 <= sdg_value < 0.85:
        return (sdg_value / 0.85) * 0.5
    return None  # For unexpected values


def create_scaled_predictions():
    try:
        # Fetch all existing predictions
        predictions = (
            session.query(SDGPrediction).filter(SDGPrediction.prediction_model.in_([PREDICTION_MODEL])).limit(5).all()
        )
        new_predictions = []

        for prediction in predictions:
            # Perform scaling for all SDG columns
            scaled_prediction = SDGPrediction(
                publication_id=prediction.publication_id,
                prediction_model=f"Scaled_{prediction.prediction_model}",
                sdg1=scale_sdg_values(prediction.sdg1),
                sdg2=scale_sdg_values(prediction.sdg2),
                sdg3=scale_sdg_values(prediction.sdg3),
                sdg4=scale_sdg_values(prediction.sdg4),
                sdg5=scale_sdg_values(prediction.sdg5),
                sdg6=scale_sdg_values(prediction.sdg6),
                sdg7=scale_sdg_values(prediction.sdg7),
                sdg8=scale_sdg_values(prediction.sdg8),
                sdg9=scale_sdg_values(prediction.sdg9),
                sdg10=scale_sdg_values(prediction.sdg10),
                sdg11=scale_sdg_values(prediction.sdg11),
                sdg12=scale_sdg_values(prediction.sdg12),
                sdg13=scale_sdg_values(prediction.sdg13),
                sdg14=scale_sdg_values(prediction.sdg14),
                sdg15=scale_sdg_values(prediction.sdg15),
                sdg16=scale_sdg_values(prediction.sdg16),
                sdg17=scale_sdg_values(prediction.sdg17),
                predicted=True,  # Mark as predicted
                last_predicted_goal=prediction.last_predicted_goal,
            )
            new_predictions.append(scaled_prediction)

        print(new_predictions)
        # Add all new scaled predictions to the session
        # session.add_all(new_predictions)

        # Commit to the database
        # session.commit()
        # print(f"Successfully created {len(new_predictions)} scaled predictions.")
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()


def main():
    Base.metadata.create_all(mariadb_engine)

    create_scaled_predictions()


if __name__ == "__main__":
    main()
