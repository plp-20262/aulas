# Contador Algora v3 implementado como *objeto* (um registro de closures). A
# adição de registros a Algora (versão v3), de fato, viabiliza objetos na
# linguagem. O objeto/registro reúne todos os métodos públicos e usa o
# mecanismo de acesso a campos como forma de "dispatch" implícito, já que o
# próprio nome do campo dá acesso a cada método. As variáveis definidas em
# Contador() viram dados encapsulados (não visíveis fora do objeto) e campos no
# registro viram dados públicos. A "classe" é apenas um design pattern usado
# para construir objetos é representada aqui pela função Contador().

def Contador() {
    var objeto := {};
    var n := 0;
    objeto.update := fn (valor) { n := valor; n };
    objeto.inc := fn () { n := n + 1; n };
    objeto.dec := fn () { n := n - 1; n };
    objeto.get := fn () { n };
    objeto
}

# cria dois contadores
var c1 := Contador();
var c2 := Contador();

# observe que `c1.metodo` é a expressão que dá acesso a uma função
# enclausurada em um objeto, junto com suas próprias variáveis (neste caso
# apenas `n`, mas nada impede de haver outras)
c1.inc();

# vamos mandar várias mensagens pros objetos
# agora dizemos: vamos invocar vários métodos dos objetos
c1.inc();
c1.inc();
c1.inc();
c1.inc();
c1.dec();
c1.dec();
c1.inc();
c2.inc();
c2.inc();
c2.inc();
c2.inc();
c2.inc();

# a mensagem `get` é nossa forma de ler o valor de `n`
c2.update(25);
c1.update(7);
c1.get() + 1000 * c2.get()

# Exercício: adicione uma mensagem add ao contador que permita
# adicionar um valor `v` a `n`.
