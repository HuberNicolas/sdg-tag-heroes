export function trimValue(num) {
  return num.toString().match(/^(\d+\.\d{2})/)?.[1] || num.toFixed(2);
}
