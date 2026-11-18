# criaContador é uma função de alta ordem pq retorna um lambda/closure
def criaContador() {
    var n := 0;

    fn () {           # o corpo do closure, contudo, "enclausura" o valor de n
        n := n + 1;   # como n é mutável em Algora, se o closure executar, n é atualizado!
        n             # a cada invocação, o novo n é retornado
    }
}

var c1 := criaContador();   # c1 é um closure com n igual a 0
var c2 := criaContador();   # c2 é outro closure com n igual a 0 (mas é outro n!)

c1();            # invocamos o closure! logo, o n de c1 agora é 1
c1();            # mais uma vez: o n de c1 é 2
c1();            # outra vez: o n de c1 é 3
var v1 := c1();  # e ainda mais uma: n de c1 é 4; e v1 é uma referência para o valor

c2();            # invocamos o closure c2; primeira vez, logo n é 1
var v2 := c2();  # mais uma invocação; logo n é 2; e v2 é ref para o valor

v1 + v2   # soma os valores de v1 (4) e de v2 (2) -> 6
