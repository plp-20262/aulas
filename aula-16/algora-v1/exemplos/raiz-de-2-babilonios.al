def twice(f) {
  fn (x) {
    f(f(x))
  }
}
var passo := fn (x) { (x + 2 / x) / 2 };
twice(twice(twice(passo)))(1)
