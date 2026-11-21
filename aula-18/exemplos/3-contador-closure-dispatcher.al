# Contador Algora baseado em um dispatcher de closures + estado/mutação. Desta
# vez, o closure retornado por `Contador()` é um _dispatcher_: uma função
# intermediária que dá acesso a várias funções que, por sua vez, são os
# closures que alteram e acessam o dado `n` enclausurado (funções INC, DEC e
# GET). Para selecionar qual função, o _dispatcher_ recebe um argumento
# chamado historicamente de "mensagem" que identifica qual das funções deve ser
# escolhida e retornada para o código cliente.
#
# IMPORTANTE: como só temos números em Algora, optei por definir constantes
# para as mensagens: inc, dec e get. Também defini `ERRO` para poder forçar um
# erro de tempo de execução, necessário quando a mensagem não é reconhecida.
var inc := 0;
var dec := 1;
var get := 2;

var ERRO := fn () { 1 / 0 };

def Contador() {
    var n := 0;

    def INC() { n := n + 1; n }
    def DEC() { n := n - 1; n }
    def GET() { n }

    # Contador retorna um dispatcher…
    fn (mensagem) {
        if mensagem == inc { INC }
        else { if mensagem == dec { DEC } 
        else { if mensagem == get { GET } 
        else { ERRO() }}}
    }
}


var c1 := Contador();
var c2 := Contador();
# E ao invocarmos o contador com uma mensagem como argumento,
# isso nos permite "selecionar" uma das funções disponíveis
# associadas às mensagens. Com a mensagem `inc` selecionamos a
# função `fn () { n := n + 1; n }` acima (confira o código).
# Logo, se a invocamos, executamos o código acima e atualizamos
# o valor do `n` que está "enclausurado" na função.
c1(inc)();

# vamos mandar várias mensagens pros objetos
c1(inc)();
c1(inc)();
c1(inc)();
c1(inc)();
c1(dec)();
c1(dec)();
c1(inc)();
c2(inc)();
c2(inc)();

# a mensagem `get` é nossa forma de ler o valor de `n`
c1(get)() + 1000 * c2(get)()

# Exercício: adicione uma mensagem add ao contador que permita a qualquer
# momento adicionar um valor `v` ao dado enclausurado `n`.
