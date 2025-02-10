import hashlib
import numpy as np

# Define scoring function parameters
X = 20  # Initial starting score
alpha = 2  # Confidence influence in bootstrap
beta = 1  # Confidence influence in interest
lambda_ = 0.05  # Slower decay rate of bootstrap to keep higher initial scores
mu = 0.25  # Faster growth rate of interest-based score
L_max = 3  # Maximum luck effect
N_luck = 8  # Peak of the luck effect in vote count
sigma = 4  # Controls spread of the luck effect
offset = 10  # Ensures non-negative values


def deterministic_luck(N: int, P_max: float) -> float:
    """
    Generates deterministic luck using hashing, ensuring varied but consistent luck effects.

    Args:
        N (int): Number of votes.
        P_max (float): Maximum confidence value in votes.

    Returns:
        float: Luck-based adjustment factor.
    """
    hash_input = f"{N}-{P_max}".encode()
    hash_value = int(hashlib.sha256(hash_input).hexdigest(), 16) % 1000  # Convert hash to int
    scaled_value = 0.9 + (hash_value / 1000) * 0.2  # Scale to range [0.9, 1.1]
    return (L_max * np.exp(-((N - N_luck) / sigma) ** 2) * scaled_value) + offset  # Offset avoids negative values


def score(N: int, P_max: float) -> int:
    """
    Computes a dynamic score for SDG user labels based on voting behavior.

    Args:
        N (int): Number of votes cast.
        P_max (float): Maximum probability confidence of votes.

    Returns:
        int: Computed score.
    """
    S_B = X * (P_max ** alpha) * np.exp(-lambda_ * N)  # Initial confidence, slow decay
    S_I = X * (1 - np.exp(-mu * N)) * (P_max ** beta)  # Interest-based scoring

    # U-shape adjustment: Fast drop at 4-6 votes, rises again at 8-13
    U_S = ((0.4 * X) - X) * np.exp(-((N - 5) / 1.5) ** 2) + ((1.2 * X) - 0.4 * X) * np.exp(-((N - 10) / 3) ** 2)

    # Apply deterministic luck effect
    S_L = deterministic_luck(N, P_max)

    return max(round(S_B + S_I + U_S + S_L), 0)
