# função de alta ordem clássica: compose 
def compose(f, g) {      # esta função recebe duas funções como argumento: f e g …
  fn (x) { f(g(x)) }     # … e retorna outra função como resultado
}                        # … mas o corpo guarda os valores de f e g => é um closure

var inc := fn (x) { x + 1 };    # inc é uma função que soma 1 a n
var dobro := fn (x) { x * 2 };  # dobro é uma função que duplica n
var f := compose(inc, dobro);   # f é o closure retornado por compose, em que f é inc e g é dobro
var g := compose(dobro, inc);   # g é o closure em que f é dobro e g é inc

f(5) + g(5)
