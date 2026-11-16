def multiplicador(fator) {
  fn (n) {
    n * fator
  }
}

var dobro := multiplicador(2);
var triplo := multiplicador(3);

dobro(triplo(5))
