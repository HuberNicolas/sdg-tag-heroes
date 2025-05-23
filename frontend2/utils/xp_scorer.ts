// Define parameters
const X = 20;         // Initial starting score (adjustable)
const alpha = 1.5;      // Confidence influence in bootstrap
const beta = 8;       // Confidence influence in interest
const lambda_ = 0.5; // Slower decay rate of bootstrap to keep higher initial scores
const mu = 0.01;      // Faster growth rate of interest-based score
const L_max = 2      // Maximum luck effect
const N_luck = 4;     // Peak of the luck effect in vote count
const sigma = 3;      // Controls spread of the luck effect
const offset = 10;    // No negative values

async function deterministicLuck(N, P_max) {
  /**
   * Generates deterministic luck using hashing, ensuring varied but consistent luck effects.
   */
  const hashInput = `${N}-${P_max}`;

  const encoder = new TextEncoder();
  const data = encoder.encode(hashInput);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

  const hashValue = parseInt(hashHex, 16) % 1000;
  const scaledValue = 0.9 + (hashValue / 1000) * 0.2;

  const squareTerm = (-((N - N_luck) / sigma)) * (-((N - N_luck) / sigma));
  return (L_max * Math.exp(squareTerm) * scaledValue) + offset;
}

export async function score(N, P_max) {
  /**
   * Computes a dynamic score for SDG user labels based on voting behavior.
   */
    // Adjusted Bootstrap Score (S_B) - Slower decay
  const S_B = X * Math.pow(P_max, alpha) * Math.exp(-lambda_ * N);

  // Adjusted Interest-Based Score (S_I) - Faster growth
  const S_I = X * (1 - Math.exp(-mu * N)) * Math.pow(P_max, beta);

  // Enhanced U-Shape Adjustment (U_S)
  const U_S = ((0.5 * X) - X) * Math.exp(-Math.pow((N - 5) / 1.8, 2)) +  // Dip at 5
    ((1.5 * X) - 0.5 * X) * Math.exp(-Math.pow((N - 10) / 2.5, 2)); // Boost at 10

  // Apply deterministic luck effect
  const S_L = await deterministicLuck(N, P_max);

  return Math.round(Math.max(S_B + S_I + U_S + S_L, 0));
}

