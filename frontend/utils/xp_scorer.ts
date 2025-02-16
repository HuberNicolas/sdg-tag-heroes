// Define parameters
const X = 20;         // Initial starting score (adjustable)
const alpha = 2;      // Confidence influence in bootstrap
const beta = 1;       // Confidence influence in interest
const lambda_ = 0.05; // Slower decay rate of bootstrap to keep higher initial scores
const mu = 0.25;      // Faster growth rate of interest-based score
const L_max = 3;      // Maximum luck effect
const N_luck = 8;     // Peak of the luck effect in vote count
const sigma = 4;      // Controls spread of the luck effect
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
  const S_B = X * (P_max * P_max) * Math.exp(-lambda_ * N);  // Using P_max^2 instead of P_max^alpha

  const S_I = X * (1 - Math.exp(-mu * N)) * P_max;

  // U-shape adjustment: Fast drop at 4-6 votes, rises again at 8-13
  const U_S = ((0.4 * X) - X) * Math.exp(-((N - 5) / 1.5) * ((N - 5) / 1.5)) +
    ((1.2 * X) - 0.4 * X) * Math.exp(-((N - 10) / 3) * ((N - 10) / 3));

  // Apply deterministic luck effect
  const S_L = await deterministicLuck(N, P_max);

  return Math.round(Math.max(S_B + S_I + U_S + S_L, 0));
}

