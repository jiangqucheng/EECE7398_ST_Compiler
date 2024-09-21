/**
 * Calculates the Fibonacci sequence up to the given number.
 * 
 * @param n - The number up to which the Fibonacci sequence should be calculated.
 * @returns The Fibonacci number at the given position.
 */
function fibonacci(n: number): number {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

/**
 * Prints the Fibonacci series up to a given count.
 * 
 * @param count - The number of Fibonacci numbers to print.
 * @returns void
 */
function printFibonacciSeries(count: number): void {
    for (let i = 0; i < count; i=i+1) {
        let fib: number = fibonacci(i);
        console.log(i, fib);
    }
}

printFibonacciSeries(10);