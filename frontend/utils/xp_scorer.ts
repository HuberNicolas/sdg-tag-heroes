import crypto from 'crypto';

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

// Function to generate deterministic luck using hashing
function deterministicLuck(N: number, P_max: number): number {
  const hashInput = `${N}-${P_max}`;
  const hash = crypto.createHash('sha256').update(hashInput).digest('hex');
  const hashValue = parseInt(hash.slice(-3), 16) % 1000; // Convert hash to int
  const scaledValue = 0.9 + (hashValue / 1000) * 0.2; // Scale to range [0.9, 1.1]
  return Math.max((L_max * Math.exp((-((N - N_luck) / sigma)) ** 2) * scaledValue) + offset, 5); // Ensure minimum luck contribution
}

// Define the function with a true U-shape: min at 4-6 votes, rising by 8-13
function score(N: number, P_max: number): number {
  const S_B = X * (P_max ** alpha) * Math.exp(-lambda_ * N);  // High initial score, slow decay
  const S_I = X * (1 - Math.exp(-mu * N)) * (P_max ** beta);  // Low start, growing interest

  // U-shape adjustment: Fast drop to ~0.4X at 4-6, rise to 1X/1.2X at 8-13
  const U_S = Math.max(((0.4 * X) - X) * Math.exp(-((N - 5) / 1.5) ** 2) + ((1.2 * X) - 0.4 * X) * Math.exp(-((N - 10) / 3) ** 2), 0);

  // Deterministic Luck effect
  const S_L = deterministicLuck(N, P_max);

  return Math.max(S_B + S_I + U_S + S_L, 10); // Ensure total score is always at least 10
}
