# Contador Algora baseado em closure e estado/mutação.
# Usando um closure, enclausuramos uma variável (`n`) em um closure.
# E esse closure é usado para atualizar o contador e para consultá-lo.
#
# IMPORANTE: embora o código possa ser visto como funcional, não dá pra dizer
# que é funcional "puro", justamente porque temos estado e mutação envolvidos.
# Veja que o closure não tem transparência referencial: cada invocação tem efeito
# e retorna valores diferentes! É o preço a pagar.

def criaContador() {
    var n := 0;
    fn () {
        n := n + 1;
        n
    }
}

var c1 := criaContador();
var c2 := criaContador();

c1();
c1();
c1();
c2();

c1() + c2()
