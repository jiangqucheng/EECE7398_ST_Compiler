# Part 1: Benchmark and run in Bril

## Prerequisite

Before running any make rules, ensure the required tools are available in the environment. Please check the [repo Readme](https://github.com/jiangqucheng/EECE7398_ST_Compiler/blob/main/README.md) which is located in the root directory of this repo for instructions on setting up the environment. Once the environment is set up, you can use the following command to run a check of the required tools:

```bash
make check-tools
```

## Workflow

Benchmarks in this HW are written in Typescript. The path to generate all kinds of stuff are showing in the following graph. 

```mermaid
%%{init: {"flowchart": {"htmlLabels": false}} }%%

%%| echo: false 
graph TB;
TS("TypeScript (*.ts)")
BJ("Bril in Json (*.bril.json)")
BT("Bril in TXT (*.bril)")
BI["Runtime Exec"]

BT --bril2json--> BJ
BJ --bril2txt--> BT
TS --ts2bril--> BJ;
BJ --brili--> BI;
```


## Workflow: Generate bril code in json/txt format

To generate bril code in json/txt format, you can use the following two commands.

```bash
make benchmark/<TARGET>.bril.json  # bril in json format
make benchmark/<TARGET>.bril       # bril in txt format
# TARGET can be `euler`, `fibonacci`
```

## Workflow: Run tests

By following these steps and using the Makefile, you can easily generate bril code in json/txt format and run tests to validate the generated code.

```bash
make run          # run all benchmarks
make run_<TARGET> # run specified benchmark: <TARGET>
make turnt        # benchmark check using turnt 
make              # default: run all + turnt check
```

## Benchmark: `euler`

This TypeScript code (`benchmark/euler.ts`) defines three functions: `app_main`, `factorial`, and `taylor_series_euler`. These functions work together to compute an approximation of Euler's number (e) using the Taylor series expansion.

The `app_main` function serves as the entry point of the program. It takes a single argument `n`, which determines the number of terms to include in the Taylor series approximation. Inside this function, the `taylor_series_euler` function is called with `n` as its argument, and the result is stored in the variable `e`. Finally, the value of `e` is printed to the console.

The `factorial` function is a recursive function that calculates the factorial of a given number `n`. The factorial of a number is the product of all positive integers up to that number. The base case for the recursion is when `n` is less than or equal to 1, in which case the function returns 1. For other values of `n`, the function calls itself with `n-1` and multiplies the result by `n`.

The `taylor_series_euler` function computes the approximation of Euler's number using the Taylor series expansion. It initializes a variable `e` to `0` and iterates from `0` to `n-1`. In each iteration, it adds the reciprocal of the factorial of the current index `i` to `e`. This process accumulates the sum of the series terms, which approximates Euler's number. After the loop completes, the function returns the computed value of `e`.

Finally, the `app_main` function is called with the argument 10, which means the program will compute the approximation of Euler's number using the first 10 terms of the Taylor series and print the result to the console.

## Benchmark: `fibonacci`

This TypeScript code (`benchmark/fibonacci.ts`) defines two functions: `fibonacci` and `printFibonacciSeries`. These functions work together to calculate and print the Fibonacci sequence up to a specified number of terms.

The `fibonacci` function calculates the Fibonacci number at a given position `n`. The Fibonacci sequence is a series of numbers where each number is the sum of the two preceding ones, usually starting with 0 and 1. The function uses a recursive approach to compute the Fibonacci number. If `n` is less than or equal to 1, the function returns `n` directly, as the first two numbers in the Fibonacci sequence are 0 and 1. For other values of `n`, the function calls itself with `n-1` and `n-2` and returns the sum of these two calls. This recursive approach effectively builds the Fibonacci sequence by breaking down the problem into smaller subproblems.

The `printFibonacciSeries` function prints the Fibonacci series up to a given count. It takes a single parameter `count`, which specifies the number of Fibonacci numbers to print. The function uses a `for` loop to iterate from 0 to `count-1`. In each iteration, it calls the `fibonacci` function to compute the Fibonacci number at the current index `i` and stores the result in the variable `fib`. It then prints the index `i` and the corresponding Fibonacci number `fib` to the console. This function provides a way to visualize the Fibonacci sequence by printing each term along with its position in the sequence.

Finally, the `printFibonacciSeries` function is called with the argument 10, which means the program will print the first 10 numbers in the Fibonacci sequence. This call demonstrates the functionality of both the `fibonacci` and `printFibonacciSeries` functions, showing how they work together to compute and display the Fibonacci sequence.
