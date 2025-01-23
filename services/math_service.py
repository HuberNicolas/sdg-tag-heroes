import math
from typing import List
import statistics

class MathService:
    """
    A service for performing mathematical and statistical calculations.
    """

    @staticmethod
    def calculate_entropy(values: List[float]) -> float:
        """
        Calculate the entropy of a list of values.

        Args:
            values (List[float]): A list of values (e.g., SDG prediction values).

        Returns:
            float: The entropy of the values.
        """
        total = sum(values)
        if total == 0:
            return 0.0

        # Normalize the values to form a probability distribution
        probabilities = [value / total for value in values if value > 0]

        # Calculate entropy
        entropy = -sum(p * math.log(p, 2) for p in probabilities)
        return entropy

    @staticmethod
    def calculate_standard_deviation(values: List[float]) -> float:
        """
        Calculate the standard deviation of a list of values.

        Args:
            values (List[float]): A list of values.

        Returns:
            float: The standard deviation of the values.
        """
        return statistics.stdev(values)
