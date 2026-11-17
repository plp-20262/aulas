def fatorial(n) {
  if n == 0 { 
    1 
  } else {
    n * fatorial(n - 1)
  }
}

fatorial(7)
