from typing import List, Dict, Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import SDGPrediction
from services.math_service import MathService
from settings.settings import SDGPredictionsRouterSettings

sdg_predictions_router_settings = SDGPredictionsRouterSettings()


class MetricsService:
    def __init__(self, math_service: MathService):
        """
        Initialize the MetricsService with a MathService dependency.

        Args:
            math_service (MathService): A service for performing mathematical calculations.
        """
        self.math_service = math_service

    def get_distribution_metrics_by_publication_ids(
        self, publication_ids: List[int], db: Session
    ) -> List[Dict[str, Any]]:
        """
        Calculate distribution metrics (entropy and standard deviation) for a list of publication IDs.

        Args:
            publication_ids (List[int]): List of publication IDs.
            db (Session): Database session.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing publication ID, entropy, and standard deviation.
        """
        # Query SDG predictions for the given publication IDs
        sdg_predictions = (
            db.query(SDGPrediction)
            .filter(SDGPrediction.publication_id.in_(publication_ids))
            .all()
        )

        # Filter the SDG predictions by prediction_model
        default_model_predictions = [
            prediction for prediction in sdg_predictions
            if prediction.prediction_model == sdg_predictions_router_settings.DEFAULT_MODEL
        ]

        if not default_model_predictions:
            raise HTTPException(
                status_code=404,
                detail=f"No SDG predictions found for the provided publication IDs."
            )

        # Calculate metrics for each prediction
        results = []
        for prediction in default_model_predictions:
            sdg_values = self._extract_sdg_values(prediction)
            entropy = self.math_service.calculate_entropy(sdg_values)
            sd = self.math_service.calculate_standard_deviation(sdg_values)

            results.append({
                "publication_id": prediction.publication_id,
                "entropy": entropy,
                "standard_deviation": sd,
            })

        return results

    def get_publication_metrics_by_id(
        self, publication_id: int, db: Session
    ) -> Dict[str, Any]:
        """
        Fetch the entropy and standard deviation for the SDG prediction values of a specific publication.

        Args:
            publication_id (int): The ID of the publication.
            db (Session): Database session.

        Returns:
            Dict[str, Any]: A dictionary with entropy and standard deviation of the predictions.
        """
        # Fetch the SDG predictions for the publication
        sdg_predictions = (
            db.query(SDGPrediction)
            .filter(SDGPrediction.publication_id == publication_id)
            .all()
        )

        # Filter the SDG predictions by prediction_model
        default_model_prediction = [
            prediction for prediction in sdg_predictions
            if prediction.prediction_model == sdg_predictions_router_settings.DEFAULT_MODEL
        ]

        if not default_model_prediction:
            raise HTTPException(
                status_code=404,
                detail=f"SDG predictions for publication ID {publication_id} not found."
            )

        # Extract the first (and only) prediction from the list
        sdg_prediction = default_model_prediction[0]

        # Calculate entropy and standard deviation
        sdg_values = self._extract_sdg_values(sdg_prediction)  # Pass the single prediction object
        entropy = self.math_service.calculate_entropy(sdg_values)
        sd = self.math_service.calculate_standard_deviation(sdg_values)

        return {
            "publication_id": publication_id,
            "entropy": entropy,
            "standard_deviation": sd,
        }

    def get_publications_by_metric(
        self, metric_type: str, order: str, top_n: int, db: Session
    ) -> List[Dict[str, Any]]:
        """
        Fetch the top or bottom N publications based on entropy or standard deviation.

        Args:
            metric_type (str): The metric type to rank by ("entropy" or "standard_deviation").
            order (str): Specify "top" for highest or "bottom" for lowest.
            top_n (int): Number of results to return.
            db (Session): Database session.

        Returns:
            List[Dict[str, Any]]: List of dictionaries with publication ID, metric value, and metric type.
        """
        # Validate metric type
        if metric_type not in {"entropy", "standard_deviation"}:
            raise HTTPException(
                status_code=400,
                detail="Invalid metric type. Allowed values are 'entropy' or 'standard_deviation'."
            )

        # Validate order
        if order not in {"top", "bottom"}:
            raise HTTPException(
                status_code=400,
                detail="Invalid order value. Allowed values are 'top' or 'bottom'."
            )

        # Validate top_n
        if top_n <= 0:
            raise HTTPException(
                status_code=400,
                detail="Invalid top_n value. It must be a positive integer."
            )

        # Query all SDG predictions
        sdg_predictions = db.query(SDGPrediction).filter(
            SDGPrediction.prediction_model == sdg_predictions_router_settings.DEFAULT_MODEL
        ).all()

        if not sdg_predictions:
            raise HTTPException(
                status_code=404,
                detail="No SDG predictions found."
            )

        # Calculate metrics for each prediction
        metrics = []
        for prediction in sdg_predictions:
            sdg_values = self._extract_sdg_values(prediction)
            entropy = self.math_service.calculate_entropy(sdg_values)
            sd = self.math_service.calculate_standard_deviation(sdg_values)

            metrics.append({
                "publication_id": prediction.publication_id,
                "entropy": entropy,
                "standard_deviation": sd,
            })

        # Sort by the specified metric in the correct order
        reverse_order = order == "top"
        sorted_results = sorted(
            metrics, key=lambda x: x[metric_type], reverse=reverse_order
        )[:top_n]

        # Add metric type and order to the response for clarity
        for entry in sorted_results:
            entry["metric_type"] = metric_type
            entry["order"] = order

        return sorted_results

    def _extract_sdg_values(self, prediction) -> List[float]:
        """
        Extract SDG values from a prediction object.

        Args:
            prediction: An SDGPrediction object.

        Returns:
            List[float]: A list of SDG values.
        """
        return [
            prediction.sdg1, prediction.sdg2, prediction.sdg3, prediction.sdg4,
            prediction.sdg5, prediction.sdg6, prediction.sdg7, prediction.sdg8,
            prediction.sdg9, prediction.sdg10, prediction.sdg11, prediction.sdg12,
            prediction.sdg13, prediction.sdg14, prediction.sdg15, prediction.sdg16,
            prediction.sdg17
        ]
