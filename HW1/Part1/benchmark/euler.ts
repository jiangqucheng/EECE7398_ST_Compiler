/**
 * The main function of the application.
 * 
 * @param n - The number of iterations for the Euler's method.
 */
function app_main(n: number) {
  var e: number = taylor_series_euler(n);
  console.log(e);
}

/**
 * Calculates the factorial of a given number.
 * 
 * @param n - The number to calculate the factorial for.
 * @returns The factorial of the given number.
 */
function factorial(n: number): number {
  if(n <= 1) {
    return 1;
  }
  return factorial(n-1)*n;
}

/**
 * Calculates the approximation of Euler's number using Taylor series.
 * 
 * @param n - The number of terms to include in the series.
 * @returns The approximation of Euler's number.
 */
function taylor_series_euler(n: number): number {
  var e: number = 0;
  for(let i = 0; i < n; i=i+1) {
    e = 1 / factorial(i) + e;
  }
  return e;
}

app_main(10);