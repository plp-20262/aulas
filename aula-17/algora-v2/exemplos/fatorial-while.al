def fatorial(n) {
  var fat := 1;
  while 0 < n {
    fat := fat * n;
    n := n - 1;
  }
  fat
}

fatorial(6)
