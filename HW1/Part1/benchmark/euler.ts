function app_main(n: number) {
  var e: number = taylor_series_euler(n);
  console.log(e);
}

function factorial(n: number): number {
  if(n <= 1) {
    return 1;
  }
  return factorial(n-1)*n;
}

function taylor_series_euler(n: number): number {
  var e: number = 0;
  for(let i = 0; i < n; i=i+1) {
    e = 1 / factorial(i) + e;
  }
  return e;
}

app_main(10);