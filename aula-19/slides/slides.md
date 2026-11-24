---
title: "Modelagem de Dados"
subtitle: "Unidade 7 / Aula 19<br>Tipos Algébricos de Dados vs Orientação a Objetos"
author: "Dalton Serey"
date: "23 de novembro de 2026"
pagetitle: "Aula 19 — Closures × objetos, encapsulamento e o problema da expressão"
lang: pt-BR
theme: white
center: false
hash: true
controls: false
progress: false
transition: none
margin: 0.03
---

## Na aula passada…

..adicionamos suporte a [registros]{.highlight} (ou
_records_) a Algora… e vimos que isso combinado ao que
já tínhamos na LP nos garantiu o essencial da
[Orientação a Objetos]{.highlight} na 
linguagem.

. . .

### Nesta aula vamos discutir… 

1. Quais das características essenciais da Orientação a Objetos estão, de fato, presentes em Algora com a adição de _records_?
2. Como se comparam as estratégias de modelagem de dados compostos com TADs e com OO?

::: notes
⏱ 2 min.

Nesta aula
não há construção nova de linguagem. Não vou introduzir
novas _features_, nem apresentarei qualquer nova formalização. Vamos apenas apreciar em mais detalhes
o que acabamos de construir. Quais as caracterísitcas
dessas linguagens e como se comparam entre si e com
linguagens reais.
:::

## Retomando a Aula 18

**objeto** = closure + estado mutável + record

> 1. [closures com escopo léxico]{.highlight} permite combinar variáveis e métodos;

> 2. [estado e mutação]{.highlight} permitem que os métodos atualizem as variáveis;

> 3. [registros]{.highlight} nos dão a [dot notation]{.highlight} e simplificam o [dispatch]{.highlight}.

. . .

::: notes
⏱ 2 min.

Relembre a Aula 18: progredimos de um simples contador feito como um closure, passamos por uma segunda implementação com um _dispatcher_ explícito de closures e, por fim, introduzimos _records_ e implementamos objetos como registros de closures que encapsulam (ou _enclausuram_) dados.

Lembrete sobre os exemplos: Algora e Aljabr só têm
números. Então tanto nomes, como sons de animais serão códigos numéricos.
:::

## O contador como objeto

```algora
def Contdor() {
    var n := 0;
    var obj := {};
    obj.inc := fn () { n := n + 1; n };
    obj.get := fn () { n };
    obj
}

var c1 := Contador();
var c2 := Contador();
c1.inc();
c1.inc();
c2.inc();
c1.get() + c2.get()        # -> 3
```
. . .

Aqui temos o básico da OO: [identidade]{.highlight} + [estado]{.highlight} + [comportamento]{.highlight}!

::: notes
⏱ 4 min.

Este código é o mesmo que vimos na aula anterior. Nele,
a função `Contador()` é o construtor da "classe". Ele
cria dados privados (`n`); cria o registro (`obj`);
popula o registro com os closures `inc` e `get`; e, por
fim, retorna o registro como resultado.
:::

## Mas onde está o estado?

```text
Ambiente               Store

ambiente criado no código cliente:
c1 ─────> ℓ₁ ─────> registro { inc ↦ closure₁, get ↦ closure₂ }

ambiente criado por Contador() (capturado pelas closures):
n ──────> ℓ₂ ─────> 2
```

O estado está dividido entre o [ambiente]{.highlight} e o [store]{.highlight}.

. . .

#### O que objetos/records acrescentam a _closures_ simples?

1. permitem combinar múltipos métodos com um **mesmo** estado
2. nos dão **identidade** única por objeto (o que faria `var c3 := c1;`?)
3. permitem a **leitura** e a **mutação** do estado interno.

::: notes
⏱ 4 min.

A figura é uma simplificação. Diretamente, o
objeto/_record_ guarda só os métodos; `n` vive em outra
localização, alcançável apenas pelas closures. Esse
detalhe é o centro da próxima seção.

Resposta: não há mecanismo novo. O método **é** uma closure (Unidade 4); a diferença está em como combinamos as construções que já existiam.
:::

## Nossa OO suporta duas formas de estado {.small style="--code-scale: 0.90"}

```algora
def Contador() {
    var n := 0;      # n está no ambiente acessível apenas via closures
    var obj := {};
    obj.inc := fn () { n := n + 1; n };
    obj.get := fn () { n };
    obj
}
```
Algora nos permite expressar campos [privados]{.highlight} e [públicos]{.highlight}.

. . .
```algora
def ContadorPublico() {
    var obj := { n: 0 };    # obj.n é público e acessível via registro!
    obj.inc := fn () { obj.n := obj.n + 1; obj.n };
    obj.get := fn () { obj.n };
    obj
}
```

::: notes
⏱ 6 min.

Aqui nosso primeiro _corolário_: Algora admite campos
públicos e campos privados. Já tínhamos visto que
variáveis na função só estão disponíveis dentro dela e
nos closures/métodos. Mas observe que se colocamos
dados no registro, isso equivale a campos públicos.
:::

## E de onde vem a privacidade?

Vem da própria definição de **escopo léxico**.

- não foi necessário introduzir [nenhuma regra nova]{.highlight}
- a variável `n` só existe no ambiente criado por `Contador()`
- e só as closures criadas por `Contador()` capturam `n`
- portanto, nenhuma outra parte do código tem acesso a `n`

. . .

É importante distinguir dois conceitos:

- **agregar**: colocar dados e operações em um mesmo lugar, sob uma mesma unidade indivisível;
- **encapsular**: garantir que o acesso a dados privados se dê
apenas através de uma interface pública controlada.

. . .

É o uso de [records]{.highlight} que nos garante agregação,
mas é o uso de [closures]{.highlight} que nos garante o
encapsulamento.

::: notes
⏱ 3 min.

Pergunta antes de revelar: "não há regra de campo
privado em `algora`; de onde vem a privacidade?"

Agregar não é encapsular: `ContadorPublico` agrega; `Contador` encapsula.
Em `algora`, o programador escolhe entre as duas representações.
:::

## Invariantes {.small style="--code-scale: 0.90"}

```algora
def Conta(inicial) {
    var saldo := if inicial < 0 { 0 } else { inicial };
    var obj := {};
    obj.deposita := fn (v) {
        if v < 0 { saldo } else { saldo := saldo + v; saldo }
    };
    obj.saca := fn (v) {
        if v < 0 { saldo } else {
            if saldo < v { saldo } else { saldo := saldo - v; saldo }
        }
    };
    obj.saldo := fn () { saldo };
    obj
}
```

**Invariante**: `saldo >= 0`, para **todo** programa que usa a `Conta`. Mas e se o saldo fosse um campo público? Se usássemos `c.saldo := -1000`?

::: notes
⏱ 4 min.

Uma invariante em OO é uma condição sobre o estado de
um objeto que deve ser sempre verdadeira quando o
objeto está observável (ou em _estado estável_).
Invariantes são importantes para provar propriedades de
objetos. Para poder garantir invariantes, o encapsulamento é propriedade chave! Na prática, garantimos uma invariante por indução: a base (o construtor deve estabelecer a condição); o passo (cada método público deve preservar a condição); e por fechamento (aqui é que entra o encapsulamento: nenhum código externo deve poder alterar o estado sem passar pelos métodos).

Com saldo privado, a invariante é propriedade da
**conta**. Com saldo público, precisa depender de
**todos os usuários** da conta.
:::

## Encapsulamento nas linguagens reais

| Linguagem | Como se esconde o estado |
|---|---|
| Java | `private`, imposto pelo compilador; vale por **classe** |
| Python | convenção `_campo` |
| JavaScript | `#campo` (recente); antes, somente via closures |
| Algora | escopo léxico; vale por **objeto** |

::: notes
⏱ 3 min.

Diferença sutil Java × `algora`: em Java, o código da classe `Conta` pode
ler `outra.saldo` de **outra** conta; em `algora`, cada objeto tem seu
próprio ambiente capturado, e a privacidade é por objeto.
:::

## `this`, `self` e `obj`

| | Java | Python | JavaScript | `algora` |
|---|---|---|---|---|
| nome | `this` | `self` | `this` | `obj` |
| reservado? | sim | não | sim | **não** |
| valor definido por | compilador, na chamada | método ligado | **como** a função é chamada | escopo léxico |

::: notes
⏱ 3 min.

Em Algora, o `obj` que usamos é uma simples variável da
linguagem. Não há qualquer semântica especial para ela.
Em outras LPs, contudo, é comum haver semântica especial.

O `this` de JavaScript, nas funções comuns, não depende
de onde a função foi escrita, mas de como foi chamada.
Em termos da Unidade 4, é mais próximo de escopo
**dinâmico** do que de léxico.

Python: `o.m(x)` equivale a `C.m(o, x)`; `self` é só o
primeiro parâmetro, por convenção.
:::

## Método destacado

```algora
var c := Contador();
var f := c.inc;        # o método, sem o objeto
f();                   # 1
f();                   # 2
c.get()                # 2
```

Por que isso funciona?

. . .

Cada método é um closure: o ambiente de criação já foi fixado.

::: notes
⏱ 3 min.

Métodos destacados (ou _detached methods_) são métodos
que são "removidos" ou "independizados" de seus objetos
e usados como funções. Em Algora, _destacar_ métodos
não altera o _closure_, logo não desvincula dos dados
do objeto. O destaque é apenas sintático.
:::

## Herança e polimorfismo, sem `class` (parte 1)

```algora
def Animal(nome_dado) {
  var obj := {};
  var nome := nome_dado;
  obj.voz := fn () { SOM_GENERICO };
  obj.fale := fn () { obj.voz() };    # chama voz dinamicamente
  obj.diga_nome := fn () { nome };
  obj
}

var animal := Animal(1);
animal.fale()
```

Considere o construtor da "classe" Animal. Dos três
métodos definidos, o método `fale` é especialmente
interessante porque invoca dinamicamente o método
`voz`.

::: notes
Observe que o método `fale` apenas invoca a função `voz`.
:::

## Herança e polimorfismo, sem `class` (parte 2)

```algora
def Cachorro(nome) {
  var obj := Animal(nome);       # pai cria o registro
  obj.voz := fn () { LATIDO };   # filho muta o MESMO registro
  obj
}

def Gato(nome) {
  var obj := Animal(nome);       # mesmo padrão
  obj.voz := fn () { MIADO };
  obj
}
```

Aqui vemos como codificar [herança]{.highlight} em
Algora. O construtor da subclasse invoca o da
superclasse em vez de partir de um objeto vazio. Em
seguida, apenas o complementa. Aqui, `Cachorro` e
`Gato` definem sua própria `voz`, sobreescrevendo o
método da superclasse.

::: notes

Observe a relação conceitual que o código construtor da
subclasse estabelece ao usar o construtor da
superclasse: um `Cachorro` e um `Gato` são,
literalmente, objetos da classe `Animal`.
:::

## O código completo  {.small style="--code-scale: 0.75; --column-scale: 1"}

:::: columns
::: {.column width="50%"}
```algora
var SOM_GENERICO := 1;
var LATIDO := 2;
var MIADO := 3;

def Animal(nome_dado) {
  var obj := {};
  var nome := nome_dado;
  obj.voz := fn () { SOM_GENERICO };
  obj.fale := fn () { obj.voz() };
  obj.diga_nome := fn () { nome };
  obj
}
```

O importante aqui é observar que a única invocação a
`voz()` está dentro de `Animal`. E que mesmo assim, o
`voz()` das subclasses é invocado.
:::

::: {.column width="50%"}
```algora
def Cachorro(nome) {
  var obj := Animal(nome);
  obj.voz := fn () { LATIDO };
  obj
}

def Gato(nome) {
  var obj := Animal(nome);
  obj.voz := fn () { MIADO };
  obj
}

var animal := Animal(1);
var cachorro := Cachorro(2);
var gato := Gato(3);

animal.fale()
+ cachorro.fale() * 10
+ gato.fale() * 100
# -> 321
```
:::
::::

::: notes

É importante observar que `gato.fale()` invoca uma
função que só está definida no corpo de `Animal`, mas
que terminal por executar o código de `voz()` em
`Gato`.

Também é importante observar que `Gato` poderia ter
sido adicionada de forma totalmente independente de `Animal`. Ou seja, não há qualquer previsão de que `Gato` iria existir quando `Animal` foi criado, mas mesmo assim, a invocação de `fale()` em `Animal` terminará por invocar o método `voz()` de `Gato`.

É a isso que chamamos: _late binding_.

:::

## Ligação tardia ou _late binding_

```algora
var g := Gato();
var c := Cachorro();

g.fale();        # 3 (MIADO)
c.fale();        # 2 (LATIDO)
```

O método `fale` está contido em `Animal`, mas ele invoca
`obj.voz()` que só é corretamente definido nos registro
das subclasses (`Gato` e `Cachorro`). Observe que `gato.fale()` irá executar `fale()` definido apenas em `Animal` e ele terá que invocar `voz()` definido em `Gato`.

Este mecanismo permite que uma classe mãe (`Animal`)
invoque métodos de subclasses, mesmo que estas tenham
sido escritas depois da classe mãe. A isto se chama
[_late binding_]{.highlight} e é uma das marcas
registradas da herança em OO. E é ele que viabiliza o
[polimorfismo de subtipos]{.highlight} (é o que faz
`x.fale()` se comportar diferente para cada subtipo).

## O outro caminho: tipos algébricos (parte 1)

```aljabr
type Animal = Generico(nome) | Cachorro(nome) | Gato(nome)

let som_generico = 1 in
let latido       = 2 in
let miado        = 3 in

# operações (funções separadas dos dados)
let voz = fn (a) =>
  match a {
    Generico(_) => som_generico
    Cachorro(_) => latido
    Gato(_)     => miado
  }
in

let fale = fn (a) => voz(a) in
```

## O outro caminho: tipos algébricos (parte 1)

```aljabr
# "instâncias" (valores imutáveis)
let animal   = Generico(1) in
let cachorro = Cachorro(2) in
let gato     = Gato(3) in

fale(animal)              # -> 1
+ fale(cachorro) * 10     # -> 20
+ fale(gato) * 100        # -> 300

# -> 321
```

## Objetos × tipos algébricos

| | objetos (`algora`) | tipos algébricos (`aljabr` v4) |
|---|---|---|
| operações | **dentro** (campos) | **fora** (funções + `match`) |
| escolha da operação | leitura do campo | forma do valor |
| estado | mutável | imutável |
| representação | escondida (se quiser) | sempre visível |
| variantes | abertas | fechadas |


## O problema da expressão (Wadler 1998)

| | objetos | tipos algébricos |
|---|---|---|
| nova **variante** | fácil | difícil |
| nova **operação** | difícil | fácil |

O _expression problem_ (ou problema da expressão), cunhado por Philip Wadler em
1998, é um dilema clássico de design e sistemas de tipos em linguagens de
programação. Ele descreve a dificuldade de extender um sistema em duas
dimensões ortogonais: novos tipos de dados vs novas operações, sem modificar
o código existente e mantendo a segurança de tipos estática (em tempo de
compilação).

Voltaremos a mencionar este problema no final da unidade 8,
quando já tivermos visto sistemas de tipos. Isso nos permitirá ainda discutir
possíveis alternativas ao problema que LPs reais atuais procuram adotar.

::: notes
⏱ 5 min.

Cada estilo é fechado em uma dimensão e aberto na outra. O dilema
completo exige extensão sem alterar o código existente e sem perder
verificação de tipos (na formulação original, estática); só fará pleno
sentido depois da Unidade 8, onde voltaremos ao problema.

Qual evolução é mais comum? Depende do domínio: compilador (linguagem
estável, análises se multiplicam) favorece tipos algébricos; interface
gráfica (componentes se multiplicam) favorece objetos.

Garantias: com tipos algébricos e dados imutáveis, é mais fácil raciocinar
sobre todos os casos. Com objetos e estado mutável, o comportamento
depende do objeto e do seu estado, o que dificulta raciocínio e testes.

Soluções reais, só menção: Visitor (Java), traits (Rust, Scala), type
classes (Haskell), protocols (Swift), `functools.singledispatch` e
protocolos em Python (sem verificação estática); interfaces Java
resolvem parcialmente.
:::

## Linguagens reais {.small}

| | `algora` v3 | Java | Python | JavaScript | Rust |
|---|---|---|---|---|---|
| classes | padrão (função) | obrigatórias | valores | protótipos | não há |
| objeto | `obj` | `this` | `self` | `this` | `self` |
| estado privado | escopo léxico | `private` | `_x` | `#x` | por módulo |
| herança | copiar e sobrescrever | classes + interfaces | múltipla | protótipos | traits |
| tipos algébricos | `aljabr` v4 | `sealed` + `record` | `dataclass` + `match` | convenção | `enum` + `match` |

Algol W → Simula 67 → Smalltalk → Self · ML → Haskell → Rust

::: notes
⏱ 4 min.

Padrão geral: as linguagens modernas tendem a oferecer **os dois**
caminhos (Java ganhou `sealed`/`record`/padrões; Python, `match`; Rust
evitou herança e põe tipos algébricos no centro).

História: Algol W (records), Simula 67 (classes, objetos, herança),
Smalltalk (tudo é objeto, troca de mensagens: o dispatcher da Aula 18),
Self (protótipos; JavaScript herdou), ML (tipos algébricos, padrões).

Leituras: Reddy (1988), citado na Aula 18; Cook, *On Understanding Data
Abstraction, Revisited* (2009); Wadler (1998).
:::

## Tabela de síntese {.small}

| Linguagem | Estado | Dados | Encapsulamento | Extensibilidade |
|---|---|---|---|---|
| `aljabr` v4 | — | + soma e produto | nenhum | operação fácil · variante difícil |
| `algora` v2 | store | números + closures | variáveis capturadas | — |
| `algora` v3 | store | + records | escopo léxico, por objeto | variante fácil · operação difícil |

Mesma `aljabr` v3, dimensões **independentes**.

::: notes
⏱ 3 min.

Atualizar `tabela-design.md` com as colunas de encapsulamento e
extensibilidade. `aljabr` v4 e `algora` v3 partem da mesma `aljabr` v3 e
variam independentemente em estado e em dados. É a tese da Unidade 9:
paradigma é o conjunto de escolhas, não um rótulo.
:::

## Leituras e referências históricas (opcional)

- REDDY, Uday S. *Objects as Closures: Abstract Semantics of Object
  Oriented Languages*, 1988 (já indicado na Aula 18).
- COOK, William R. *On Understanding Data Abstraction, Revisited*,
  2009.


. . .

**Próxima aula (Unidade 8)**: os erros de hoje só aparecem **ao executar**. Dá para detectá-los antes?

::: notes
⏱ 3 min.

Gancho: `alimenta(5, 3)`, o ramo `Pot` esquecido e a leitura de campo
ausente só falham na execução. Começamos pelo fragmento aritmética +
variáveis + funções de `aljabr` v3 e voltamos à decisão A da Aula 14
(`2 + (1 < 2)`).

Exercícios de fixação: ver README.md da aula (8 exercícios, sem entrega).
:::
