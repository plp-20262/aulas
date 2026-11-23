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

Adicionamos [OO]{.highlight} a Algora… e vimos que o essencial da OO foi adicionado à linguagem pela simples adição à modelagem de dados com [registros]{.highlight}.

. . .

### Nesta aula vamos discutir… 

1. Quanto de Orientação a Objetos, de fato, adicionamos a Algora?
2. Modelagem de dados com TAD vs com OO

::: notes
⏱ 2 min.

Hoje não há construção nova de linguagem. Vamos usar o que já temos (closures,
estado, records) para compreender quanto de OO temos na LP. Com isso, fechamos
a Unidade 7 comparando os dois caminhos abertos na Aula 17: tipos algébricos
(`aljabr` v4) e objetos (`algora` v3).
:::

## Retomando a Aula 18

**objeto** = closure + estado mutável + record

> 1. [closures com escopo léxico]{.highlight} permite combinar variáveis e métodos;

> 2. [estado e mutação]{.highlight} permitem que os métodos atualizem as variáveis;

> 3. [registros]{.highlight} nos dão a [dot notation]{.highlight} e simplificam o [dispatch]{.highlight}.

. . .

::: notes
⏱ 2 min.

Aula 18: progressão closure → dispatcher → record de closures.
Hoje fechamos os três itens. Reforçar: não há regra de avaliação nova;
tudo que mostrarmos decorre das regras da Aula 18 (criação de record,
leitura e escrita de campo).

Lembrete sobre os exemplos: `algora` só tem números, então sons de animais
serão códigos (1, 2) e usaremos `tamanho()` no lugar de `mostra()`.
:::

## O contador como objeto

```text
def Contador() {
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
c1.get() + c2.get()        // 3
```
. . .

Temos o básico da OO: [identidade]{.highlight} + [estado]{.highlight} + [comportamento]{.highlight}

::: notes
⏱ 4 min.

DEMO: `exemplos/contador-privado.alg`. Mostrar também o alias:
`var c3 := c1;` e que `c3.inc()` afeta `c1`.

O "construtor" é só uma função: cria `{}`, equipa com closures, devolve.
:::

## Mas onde está o estado?

```text
Ambiente               Store

ambiente criado no código cliente:
c1 ─────> ℓ₁ ─────> registro { inc ↦ closure₁, get ↦ closure₂ }

ambiente criado por Contador() (capturado pelas closures):
n ──────> ℓ₂ ─────> 2
```

. . .

### O que objetos acrescentam a _closures_ simples?

1. permitem agrupar vários métodos com um **mesmo** estado
2. nos dão **identidade** única a cada objeto (o que faria `var c3 := c1;`?)
3. permitem a **mutação** do estado interno.

::: notes
⏱ 4 min.

A figura é simplificada. O record guarda só os métodos; `n` vive em outra
localização, alcançável apenas pelas closures. Esse detalhe é o centro
da próxima seção.

Resposta: nada de mecanismo novo. O método **é** uma closure (Unidade 4);
a diferença está em como combinamos as construções que já existiam.
:::

## Nossa OO suporta duas formas de estado {.small style="--code-scale: 0.90"}

Campos privados (encapsulamento e _information hiding_)
```text
def Contador() {
    var n := 0;
    var obj := {};
    obj.inc := fn () { n := n + 1; n };
    obj.get := fn () { n };
    obj
}
```

. . .

Campos públicos
```text
def ContadorPublico() {
    var obj := { n: 0 };
    obj.inc := fn () { obj.n := obj.n + 1; obj.n };
    obj.get := fn () { obj.n };
    obj
}
```

::: notes
⏱ 6 min.

DEMO: `exemplos/contador-privado.alg` e `contador-publico.alg`.

A célula `2 (!)`: escrever em campo inexistente **cria** o campo (é o que
fazemos com `obj.inc := ...` sobre `{}`), mas o campo novo não tem relação
com a variável `n` capturada. O estado interno continua intacto.
:::

## De onde vem a privacidade?

Do **escopo léxico**.

Não introduzimos [nenhuma regra nova]{.highlight}: a variável `n` só existe no
ambiente criado por `Contador()`, e só as closures criadas lá a capturaram.

- **agregação**: dados e operações no mesmo lugar
- **encapsular**: esconder a representação

::: notes
⏱ 3 min.

Pergunta antes de revelar: "não há regra de campo privado em `algora`;
de onde vem a privacidade?"

Agregar não é encapsular: `ContadorPublico` agrega; `Contador` encapsula.
Em `algora`, o programador escolhe entre as duas representações.
:::

## Invariantes

```text
def Conta(inicial) {
    var saldo := inicial;
    var obj := {};
    obj.deposita := fn (v) {
        if v < 0 { saldo } else { saldo := saldo + v; saldo }
    };
    obj.saca := fn (v) {
        if saldo < v { saldo } else { saldo := saldo - v; saldo }
    };
    obj.saldo := fn () { saldo };
    obj
}
```

**invariante**: `saldo >= 0`, para **todo** programa que usa a `Conta`.

E se o saldo fosse um campo público? Se usássemos `c.saldo := -1000`?

::: notes
⏱ 4 min.

DEMO: `exemplos/conta-invariante.alg`. Mostrar o ataque na versão pública.

Com saldo privado, o invariante é propriedade da **conta**. Com saldo
público, vira promessa de **todos os usuários** da conta.

Gancho: volta no Interlúdio (Aula 28), quando formos além de nomear uma
interface e perguntarmos como especificar o que ela promete.
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

O `this` de JavaScript, nas funções comuns, não depende de onde a função
foi escrita, mas de como foi chamada. Em termos da Unidade 4, é mais
próximo de escopo **dinâmico** do que de léxico.

Python: `o.m(x)` equivale a `C.m(o, x)`; `self` é só o primeiro
parâmetro, por convenção.
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

DEMO: `exemplos/metodo-destacado.alg`. Não há "objeto atual" a descobrir
na chamada: ele foi fixado na criação. Escopo léxico de novo.
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

## Herança e polimorfismo, sem `class` (parte 1)

Como codificar [herança]{.highlight} em Algora:
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

## O código {.small style="--code-scale: 0.75; --column-scale: 1"}

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

O que é importante aqui? Observe onde os métodos `fale` e `voz` são escritos e
sobreescritos. Observe onde `voz` é chamado.

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

## Ligação tardia (_late binding_)

```algora
var g := Gato();
var c := Cachorro();

g.fale();        # 3 (MIADO)
c.fale();        # 2 (LATIDO)
```

O método `fale` foi escrito em `Animal`, mas ele invoca `obj.voz()` que só é
corretamente definido nos registro das subclasses (`Gato` e `Cachorro`).

Observe que este mecanismo permite que uma classe mãe (`Animal`) invoque
métodos específicos de subclasses, mesmo que estas tenha sido escritas depois
da classe da mãe. A isto se chama _late binding_ e é uma das marcas da herança da OO.


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

## Para guardar

1. objeto = record de closures com estado compartilhado
2. privacidade vem do **escopo léxico**
3. privacidade permite **invariantes**
4. `obj` é variável comum; ligação tardia = leitura de campo
5. herança e polimorfismo: **padrões**
6. objetos × tipos algébricos: linhas × colunas
7. problema da expressão: cada estilo facilita uma evolução

### Leitura e referência histórica (opcional)

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
