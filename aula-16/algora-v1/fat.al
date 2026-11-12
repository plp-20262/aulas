def fat(n) {
  if n == 0 { 1 } else {
    n * fat(n - 1)
  }
}

fat(6) + fat(5)
