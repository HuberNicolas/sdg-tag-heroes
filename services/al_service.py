import math
from typing import List
import statistics

class ALCalculationService:
    def __init__(self):
        """
        Initialize the ALCalculationService.
        """
        pass

    @staticmethod
    def calculate_entropy(sdg_values: List[float]) -> float:
        """
        Calculate the entropy of the SDG prediction values.

        Args:
            sdg_values (List[float]): A list of prediction values for SDGs.

        Returns:
            float: The entropy of the predictions.
        """
        total = sum(sdg_values)
        if total == 0:
            return 0.0

        # Normalize the values to form a probability distribution
        probabilities = [value / total for value in sdg_values if value > 0]

        # Calculate entropy
        entropy = -sum(p * math.log(p, 2) for p in probabilities)
        return entropy

    @staticmethod
    def calculate_standard_deviation(sdg_values: List[float]) -> float:
        """
        Calculate the standard deviation of the SDG prediction values.

        Args:
            sdg_values (List[float]): A list of prediction values for SDGs.

        Returns:
            float: The standard deviation of the predictions.
        """
        return statistics.stdev(sdg_values)
