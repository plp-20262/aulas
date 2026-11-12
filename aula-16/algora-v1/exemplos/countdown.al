def conta(n) {
  if n == 0 {
    0
  } else {
    conta(n - 1)
  }
}
conta(100)
