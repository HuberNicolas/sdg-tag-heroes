export function calculateEntropy(predictions) {
  const probabilities = Object.values(predictions).filter(value => typeof value === 'number');
  const total = probabilities.reduce((sum, value) => sum + value, 0);
  const normalizedProbabilities = probabilities.map(value => value / total);

  let entropy = 0;
  normalizedProbabilities.forEach(p => {
    if (p > 0) {
      entropy -= p * Math.log(p);
    }
  });

  return entropy;
}
