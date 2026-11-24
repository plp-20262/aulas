var SOM_GENERICO := 1;
var LATIDO := 2;
var MIADO := 3;

def Animal(nome_dado) {
  var this := {};
  var nome := nome_dado;
  this.voz := fn () { SOM_GENERICO };
  this.fale := fn () { this.voz() };    # chama voz dinamicamente
  this.diga_nome := fn () { nome };
  this
}

def Cachorro(nome) {
  var this := Animal(nome);             # (1) pai cria o record
  this.voz := fn () { LATIDO };         # (2) filho muta o MESMO record
  this
}

def Gato(nome) {
  var this := Animal(nome);             # mesmo padrão
  this.voz := fn () { MIADO };
  this
}

var animal := Animal(1);
var cachorro := Cachorro(2);
var gato := Gato(3);

animal.fale()                # -> SOM_GENERICO (1) = 1
+ cachorro.fale() * 10       # -> LATIDO (2) * 10  = 20
+ gato.fale() * 100          # -> MIADO (3) * 100  = 300
# -> 321

#gato.diga_nome()             # -> 3
