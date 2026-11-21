# a função multiplicado é de alta ordem
def multiplicador(fator) {
  fn (n) {            # fn é a expressão final do corpo …
    n * fator         # … logo uma função/lambda é retornada por multiplicador
  }                   # … mas o corpo guarda o valor de `fator` => é um closure!
}

var dobro := multiplicador(2);    # dobro é um closure em que fator é 2
var triplo := multiplicador(3);   # triplo é outro closure; nele, fator é 3

dobro(triplo(5))
