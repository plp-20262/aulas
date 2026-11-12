def compose(f, g) {
  fn (x) { f(g(x)) }
}

var inc := fn (x) { x + 1 };
var dobro := fn (x) { x * 2 };
var f := compose(inc, dobro);
var g := compose(dobro, inc);
f(5) + g(5)
