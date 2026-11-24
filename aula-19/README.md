# Aula 19 — 23/Nov — Unidade 7 (3/3): closures × objetos, encapsulamento e o problema da expressão

> Tema da aula: fechar a Unidade 7 comparando os dois caminhos que
> abrimos na Aula 17 para modelar dados compostos: **tipos algébricos**
> (`aljabr` v4) e **objetos** (`algora` v3).
>
> Esta aula não introduz nenhuma construção nova de linguagem. Ela
> usa o que já temos (closures, estado mutável e records) para
> responder a duas perguntas:
>
> 1. Quais das características essenciais da orientação a objetos
>    estão, de fato, presentes em `algora` v3 com a adição de
>    *records*? E o que não está?
> 2. Como se comparam as estratégias de modelagem de dados compostos
>    com tipos algébricos e com objetos? Em particular, que preço se
>    paga em cada caso quando o programa **evolui**?
>
> - Os [slides da aula](https://plp-20262.github.io/aulas/aula-19/slides/slides.html#/title-slide) acompanham as seções 1 a 8 deste texto, no diretório [`slides/`](slides/)
> - O código completo dos exemplos está no diretório [`exemplos/`](exemplos/).


## Retomando da aula anterior

Na Aula 18 vimos que um objeto pode ser construído a partir de três
ingredientes que já tínhamos estudado separadamente:

> **objeto** = closure + estado mutável + record

- **closures** com escopo léxico (Unidade 4) permitem combinar
  variáveis e métodos;
- **estado com mutação**, graças à separação entre ambiente e store
  (Unidade 5), permite que os métodos atualizem as variáveis;
- **records**, a única novidade de `algora` v3: `{ campo: exp }`,
  `obj.campo` e `obj.campo := exp`. Eles nos dão a *dot notation* e
  simplificam o *dispatch*.

Percorremos uma progressão em três passos (closure sobre variável →
dispatcher de closures → record de closures) e deixamos, de
propósito, três itens em aberto:

1. Em um objeto, o estado fica **no record** (público) ou **numa
   variável capturada** (privado)? O que cada escolha dá ao
   programador? (Seção 2.)
2. O nome `obj` dentro do construtor faz o papel de `this` (Java) ou
   `self` (Python). Mas ele não tem regra semântica especial. O que
   isso muda? (Seção 3.)
3. Como ficaria a AST `Expr` da Aula 17 escrita em `algora`? (Esse
   item não foi apresentado em aula; ver a seção final.)

Como na aula passada, tudo o que mostramos usa apenas as regras que
já existem (a Aula 18 as introduz: criação de record, leitura e
escrita de campo). **Não há regra de avaliação nova nesta aula.** O
que há é uma tese: tudo o que chamamos de orientação a objetos
nesta aula já está implicado por essas regras.

> Uma observação sobre os exemplos. `algora` e `aljabr` só têm números
> (e closures, e records). Não temos strings nem listas. Por isso, onde
> um exemplo "real" usaria um texto, usaremos números como códigos:
> tanto os nomes dos animais quanto seus sons serão números (por
> exemplo, o latido será `2` e o miado, `3`).


## 1. Um objeto em `algora`: o que é, exatamente?

Vamos recapitular com o contador. Um objeto, para nós, é:

- uma **identidade**: um record alocado no store, que pode ser
  referenciado por vários nomes (*aliasing*, Aula 15);
- um **estado** mutável, que pode estar no próprio record ou nas
  variáveis capturadas pelos métodos;
- um **comportamento**: closures guardadas em campos do record (os
  *métodos*).

O "construtor" é apenas uma função que cria um record vazio, o
equipa com métodos e o devolve:

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
c1.get() + c2.get()        # -> 3
```

> Código: [contador-privado.alg](exemplos/contador-privado.alg)

Aqui já está o básico da OO: **identidade** + **estado** +
**comportamento**.

Compare com o ponto de partida da Unidade 7. Uma closure já agrupava
"código + dados capturados" (Unidade 4). O que objetos/records
acrescentam a closures simples?

<details>
<summary>O que um objeto acrescenta a uma closure?</summary>

Três coisas, todas visíveis no exemplo acima:

1. **Múltiplos métodos** compartilhando o mesmo estado (`inc` e `get`
   enxergam o mesmo `n`). Uma closure isolada tem uma única
   operação, ou precisa do _dispatcher_ da Aula 18.
2. **Identidade explícita**: `c1` e `c2` são objetos distintos, cada
   um com seu `n`, e `var c3 := c1;` cria um segundo nome para o
   **mesmo** objeto.
3. **Leitura e mutação do estado interno**: as chamadas sucessivas
   observam as alterações das anteriores (é o store, e não o ambiente
   capturado, que muda).

O que não muda: o mecanismo de captura é o mesmo da Unidade 4. Um
método **é** uma closure. A diferença não está em uma construção
nova, mas em como combinamos as que já existiam.
</details>

### Mas onde está o estado?

A figura abaixo (simplificada) mostra o que existe depois de
`var c1 := Contador();`:

```text
   Ambiente                          Store

   ambiente criado no código cliente:
   c1 ──────────> ℓ₁ ──────────> registro { inc ↦ closure₁,
                                            get ↦ closure₂ }

   ambiente criado por Contador() (capturado por closure₁ e closure₂):
   n ───────────> ℓ₂ ──────────> 2
```

O record guarda **somente** os métodos. O valor de `n` vive em outra
localização, alcançável apenas pelas closures. Ou seja, o estado está
dividido entre o **ambiente** e o **store**. Esse detalhe é o centro
da próxima seção.


## 2. Encapsulamento: duas representações do estado

Na Aula 18 vimos (variantes 3 e 3') que o estado de um objeto pode
ficar em dois lugares. Agora podemos compará-los com cuidado: `algora`
nos permite expressar campos **privados** e campos **públicos**.

### 2.1 Estado privado: variável capturada

É o `Contador` da seção anterior. O estado é a variável local `n`,
que só está acessível via closures. Nenhum campo do record se chama
`n`.

### 2.2 Estado público: campo do record

```text
def ContadorPublico() {
    var obj := { n: 0 };       # obj.n é público e acessível via registro!
    obj.inc := fn () { obj.n := obj.n + 1; obj.n };
    obj.get := fn () { obj.n };
    obj
}
```

> Código: [contador-publico.alg](exemplos/contador-publico.alg)

Aqui, colocar o dado no registro equivale a torná-lo um campo
público: qualquer código que tenha o objeto pode ler e escrever
`c.n`. (Na seção final há um pequeno experimento que compara o
comportamento das duas versões.)

### 2.3 E de onde vem a privacidade?

> **Pergunta:** não há regra nenhuma de "campo privado" nas regras de
> `algora`. De onde vem, então, a privacidade de `n`?
> <details>
> <summary>Clique para ver a resposta</summary>
>
> <br>Do **escopo léxico**. Não foi necessário introduzir nenhuma regra
> nova:
>
> - a variável `n` só existe no ambiente criado pela chamada a
>   `Contador()`;
> - só as closures criadas lá dentro a capturaram;
> - portanto, nenhuma expressão do programa que esteja fora do corpo
>   de `Contador` pode nomear essa variável.
>
> Não é um mecanismo a mais: é a consequência de uma decisão que
> tomamos na Unidade 4.
> </details>

### 2.4 Agregar não é encapsular

Duas ideias costumam ser confundidas:

- **Agregar**: colocar dados e operações em um mesmo lugar, sob uma
  mesma unidade indivisível (o record com campos e métodos).
  `ContadorPublico` tem isso.
- **Encapsular** (*information hiding*): garantir que o acesso a dados
  privados se dê apenas através de uma interface pública controlada.
  `Contador` tem isso.

Em `algora`, é o uso de **records** que nos garante a agregação, mas é
o uso de **closures** que nos garante o encapsulamento. O programador
escolhe entre as duas representações. Nas linguagens convencionais,
essa escolha é feita por palavras como `private`.

### 2.5 Por que isso importa: invariantes

Privacidade não é só estética. Ela permite que o objeto **garanta
propriedades** sobre o próprio estado. Considere uma conta bancária
cujo saldo nunca deve ficar negativo:

```text
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

> Código: [conta-invariante.alg](exemplos/conta-invariante.alg)

O **invariante** `saldo >= 0` vale para **todo** programa que usa uma
`Conta`. Em OO, um invariante é uma condição sobre o estado de um
objeto que deve ser sempre verdadeira quando o objeto está
observável. Garantimos um invariante por indução:

- **base**: o construtor estabelece a condição (aqui, um `inicial`
  negativo vira `0`);
- **passo**: cada método público a preserva (`deposita` e `saca`
  ignoram valores negativos, e `saca` nunca retira mais que o saldo);
- **fechamento**: nenhum código externo consegue alterar o estado sem
  passar pelos métodos. É aqui que entra o encapsulamento.

> **Pergunta:** o que acontece com o invariante se escrevermos a
> `Conta` com o saldo em um campo público (`obj.saldo := ...`) e um
> código cliente fizer `c.saldo := -1000`?
> <details>
> <summary>Clique para ver a resposta</summary>
>
> <br>Ele deixa de valer: qualquer trecho do programa pode executar
> essa atribuição. O invariante deixa de ser uma propriedade da
> **conta** e passa a ser uma promessa de **todos os usuários**
> da conta. É a mesma diferença entre confiar numa interface e
> confiar em uma convenção.
> </details>

Guarde essa observação. Ela volta no Interlúdio (Aula 28), quando
formos além de _nomear_ uma interface e perguntarmos como _especificar_
o que ela promete (contratos, invariantes).

### 2.6 Como as linguagens reais tratam isso

| Linguagem  | Como se esconde o estado                                                                 |
|------------|------------------------------------------------------------------------------------------|
| Java       | `private`, **imposto pelo compilador**; vale por **classe** (outra instância da mesma classe pode acessar) |
| Python     | convenção `_campo` (o interpretador não impede o acesso)                                 |
| JavaScript | campos `#campo` (versões recentes) ou, historicamente, somente via closures, como em `algora` |
| `algora`   | escopo léxico: a variável simplesmente não é nomeável de fora; vale por **objeto**       |

Repare na diferença sutil entre Java e `algora`: em Java, o código da
classe `Conta` pode ler `outra.saldo` de **outra** conta; em
`algora`, cada objeto tem seu próprio ambiente capturado, e a
privacidade é **por objeto**.


## 3. `this`, `self` e `obj`: um nome comum

Na Aula 18 chamamos a atenção para o fato de que o nome `obj` é uma
variável como outra qualquer: não há semântica especial para ela. Em
outras linguagens, contudo, é comum haver. Agora que temos o escopo
léxico bem estabelecido, dá para entender o que isso significa por
comparação:

| | Java | Python | JavaScript | `algora` v3 |
|---|---|---|---|---|
| Nome do "objeto atual" | `this` | `self` | `this` | `obj` (qualquer nome) |
| É palavra reservada? | sim | não (convenção; é o 1º parâmetro) | sim | **não** |
| Quem define seu valor? | o compilador, na chamada `o.m()` | o mecanismo de métodos ligados: `o.m(x)` equivale a `C.m(o, x)` | depende de **como** a função é chamada | o escopo léxico: a variável capturada na criação |

O caso de JavaScript é revelador. Nas funções comuns, o `this` não é
determinado pelo **lugar onde a função foi escrita**, mas por **como**
foi chamada. Em termos da Unidade 4, é um comportamento mais próximo
de escopo **dinâmico** do que de léxico.

### Método destacado

Em `algora`, como `obj` é uma variável capturada, o método sempre
"lembra" de qual objeto é. Experimente:

```text
var c := Contador();
var f := c.inc;        # o método, sem o objeto
f();                   # 1
f();                   # 2
c.get()                # 2
```

> Código: [metodo-destacado.alg](exemplos/metodo-destacado.alg)

*Métodos destacados* (ou *detached methods*) são métodos
"independizados" de seus objetos e usados como funções. Por que isso
funciona? Porque cada método é uma closure: o ambiente de criação já
foi fixado. O destaque é apenas sintático.

> **Pergunta:** em JavaScript, o equivalente a `const f = c.inc; f();`
> costuma falhar quando o método usa `this`. Por que, em `algora`,
> isso não acontece?
> <details>
> <summary>Clique para ver a resposta</summary>
>
> <br>Porque o método é uma closure, e a closure carrega consigo o
> ambiente de criação, no qual o objeto (ou o estado) já está
> vinculado. Não há "objeto atual" a ser descoberto na chamada: ele
> foi fixado na criação. Este é, mais uma vez, o escopo léxico
> fazendo o trabalho.
> </details>


## 4. Herança e polimorfismo, sem `class`

Herança e polimorfismo são, junto com encapsulamento, as ideias
associadas à OO. Será que `algora` v3 precisa de novas construções
para expressá-las? Vamos tentar sem nenhuma.

### 4.1 Decisão de design

Em vez de uma construção `class … extends …`, adotamos um padrão:

- o "construtor" da superclasse cria o record e o equipa com métodos;
- o construtor da subclasse **invoca o da superclasse** em vez de
  partir de um record vazio. Em seguida, apenas o complementa,
  **sobrescrevendo** os campos desejados.

### 4.2 A superclasse

```text
var SOM_GENERICO := 1;
var LATIDO := 2;
var MIADO := 3;

def Animal(nome_dado) {
    var obj := {};
    var nome := nome_dado;
    obj.voz := fn () { SOM_GENERICO };
    obj.fale := fn () { obj.voz() };       # chama voz dinamicamente
    obj.diga_nome := fn () { nome };
    obj
}

var animal := Animal(1);
animal.fale()                              # -> 1
```

Considere o construtor da "classe" `Animal`. Dos três métodos
definidos, o método `fale` é especialmente interessante porque
invoca dinamicamente o método `voz`: ele apenas lê o campo `voz` do
record e o chama.

### 4.3 As subclasses

```text
def Cachorro(nome) {
    var obj := Animal(nome);       # o pai cria o registro
    obj.voz := fn () { LATIDO };   # o filho muta o MESMO registro
    obj
}

def Gato(nome) {
    var obj := Animal(nome);       # mesmo padrão
    obj.voz := fn () { MIADO };
    obj
}
```

Aqui vemos como codificar **herança** em `algora`. O construtor da
subclasse invoca o da superclasse em vez de partir de um objeto
vazio. Em seguida, apenas o complementa: `Cachorro` e `Gato` definem
sua própria `voz`, **sobrescrevendo** o método da superclasse.

Observe a relação conceitual que o construtor da subclasse
estabelece ao usar o construtor da superclasse: um `Cachorro` e um
`Gato` são, literalmente, objetos da classe `Animal`.

### 4.4 O código completo

```text
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

> Código: [animais-oo.alg](exemplos/animais-oo.alg)

O importante aqui é observar que a **única** invocação a `voz()`
está dentro de `Animal`. E que, mesmo assim, o `voz()` das subclasses
é invocado.

### 4.5 Ligação tardia (*late binding*)

```text
var g := Gato(3);
var c := Cachorro(2);

g.fale();        # 3 (MIADO)
c.fale();        # 2 (LATIDO)
```

O método `fale` está contido em `Animal`, mas ele invoca `obj.voz()`,
que só é corretamente definido nos registros das subclasses (`Gato`
e `Cachorro`). Ou seja, `g.fale()` executa o `fale` definido apenas em
`Animal`, e este tem que invocar o `voz` definido em `Gato`.

Por que isso acontece? O `obj` capturado por `fale` é o **mesmo
record** que `Gato` recebeu e modificou. A leitura do campo `voz` é
feita **na hora da chamada**, e portanto encontra a versão do `Gato`.

Este mecanismo permite que uma classe mãe (`Animal`) invoque métodos
de subclasses, mesmo que estas tenham sido escritas **depois** da
classe mãe. Note que `Gato` poderia ter sido acrescentado de forma
totalmente independente de `Animal`: não havia qualquer previsão de
que ele existiria quando `Animal` foi escrito, mas mesmo assim o
`fale` de `Animal` termina por invocar o `voz` de `Gato`. A isto se
chama **ligação tardia** (*late binding*), ou despacho dinâmico, e é
uma das marcas registradas da herança em OO. Aqui ele é uma
consequência da regra de leitura de campo, não uma regra à parte.

É também a ligação tardia que viabiliza o **polimorfismo de
subtipos**: é o que faz `x.fale()` se comportar de modo diferente
para cada subtipo de `x`.


## 5. O outro caminho: tipos algébricos

Vamos modelar os mesmos animais em `aljabr` v4 (Aula 17). Lá não há
estado mutável nem métodos. Dados e operações ficam **separados**:

```text
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

# "instâncias" (valores imutáveis)
let animal   = Generico(1) in
let cachorro = Cachorro(2) in
let gato     = Gato(3) in

fale(animal)              # -> 1
+ fale(cachorro) * 10     # -> 20
+ fale(gato) * 100        # -> 300

# -> 321
```

> Código: [animais-adt.alj](exemplos/animais-adt.alj)

Compare as duas versões:

| | Objetos (`algora`) | Tipos algébricos (`aljabr` v4) |
|---|---|---|
| Onde estão as operações | **dentro** de cada animal (campos do record) | **fora**, em funções com `match` |
| Como se escolhe a operação | pela leitura do campo no objeto (ligação tardia) | inspecionando a **forma** do valor (`match`) |
| Estado | mutável | imutável |
| Representação | escondida (privada), se quisermos | sempre visível: qualquer função pode usar `match` |
| Variantes | abertas: qualquer um pode criar um novo "tipo" de animal | fechadas: listadas no `type` |

Repare no que acontece se quisermos acrescentar um `Passaro`. Em
`algora`, basta escrever **um construtor novo** (e `Animal`, `Gato`,
`Cachorro` ficam intactos). Em `aljabr` v4, é preciso **editar** o
`type` e a função `voz`. É o começo do problema que vamos
formalizar a seguir.


## 6. O problema da expressão

Os dois caminhos parecem resolver problemas semelhantes. Há alguma
diferença **prática** entre eles? Há, e ela aparece quando o programa
**evolui**:

|                            | Objetos (`algora`)              | Tipos algébricos (`aljabr` v4)       |
|----------------------------|---------------------------------|--------------------------------------|
| **Nova variante**          | **fácil**: um construtor novo   | **difícil**: editar `type` e todos os `match` |
| **Nova operação**          | **difícil**: editar todos os construtores | **fácil**: uma função nova    |

O *expression problem* (problema da expressão), nome dado por Philip
Wadler em 1998, é um dilema clássico de design e de sistemas de tipos
em linguagens de programação. Ele descreve a dificuldade de estender
um sistema em duas dimensões ortogonais, **novos tipos de dados** e
**novas operações**, sem modificar o código existente e mantendo a
segurança de tipos estática (em tempo de compilação). Cada estilo é
**fechado** em uma dimensão e **aberto** na outra.

Esse último requisito (a verificação estática) só fará pleno sentido
depois da Unidade 8. Voltaremos a mencionar este problema no final
dela, quando já tivermos visto sistemas de tipos, e isso nos permitirá
discutir possíveis alternativas que as linguagens reais atuais
procuram adotar.

O exemplo completo (a AST `Expr` que usamos desde a Unidade 2,
escrita nos dois estilos, com uma variante e uma operação novas)
está na seção final.

Duas consequências a notar, sem exagero:

- O que **mais** muda ao longo da vida de um programa? Novas
  variantes ou novas operações? Não há resposta universal: depende do
  domínio. Um compilador, em que a linguagem é estável e as análises
  se multiplicam, favorece tipos algébricos. Uma interface gráfica,
  em que os componentes se multiplicam e as operações básicas são
  poucas, favorece objetos.
- Os dois estilos oferecem garantias diferentes ao programador. Com
  tipos algébricos e dados imutáveis, é mais fácil raciocinar sobre
  **todos os casos** (é o que um verificador de exaustividade faz).
  Com objetos e estado mutável, o comportamento de uma chamada depende
  do objeto que a recebe **e** do estado em que ele está, o que torna
  o raciocínio e os testes mais difíceis.

### Soluções reais (apenas menção)

Muitas linguagens tentam equilibrar os dois lados. Sem entrar em
detalhes:

- o padrão de projeto _Visitor_ (Java e outras) simula "nova operação
  fácil" em um estilo orientado a objetos, ao custo de tornar "nova
  variante" mais trabalhosa;
- _traits_ (Rust, Scala), _type classes_ (Haskell) e _protocols_
  (Swift) permitem associar operações novas a tipos existentes, sem
  editar sua definição;
- Python oferece soluções parciais (`functools.singledispatch` e
  protocolos), mas sem verificação estática;
- as interfaces de Java resolvem apenas parte do problema.

Esse é um dos motivos pelos quais as linguagens modernas misturam os
dois caminhos (Seção 7).


## 7. Comparando com linguagens reais

Com o que construímos, vale posicionar `algora` v3 e `aljabr` v4
diante de linguagens que conhecemos.

| | `algora` v3 | Java | Python | JavaScript | Rust |
|---|---|---|---|---|---|
| Objetos | records de closures | instâncias de classes | instâncias de classes (guardam campos em um dicionário, `__dict__`) | objetos com protótipos | `struct` + `impl` |
| Classes | padrão de projeto (função construtora) | obrigatórias | são valores (objetos) | `class` é açúcar sobre protótipos | não há |
| Objeto atual | variável comum (`obj`) | `this` | `self` | `this` | `self` |
| Estado privado | escopo léxico | `private` (por classe) | convenção `_x` | `#campo` | por módulo |
| Herança | padrão (o construtor da subclasse reusa o da superclasse e sobrescreve) | de classes (simples) + interfaces | de classes (múltipla) | por protótipos/`class` | **não há**; usa-se `trait` |
| Tipos algébricos | via `aljabr` v4 | `sealed` + `record` + `switch` com padrões (versões recentes) | `dataclass` + `match` | convenções | `enum` + `match` (nativos) |

Observe o padrão geral: as linguagens **modernas** tendem a oferecer
**os dois** caminhos. Java foi acrescentando suporte a tipos
algébricos; Python também (`match`); Rust evitou herança e põe os
tipos algébricos no centro. Isso é um sinal de que ambos os estilos
têm vantagens reais, e de que o problema da expressão não tem solução
única.

### Um pouco de história

```text
Algol W → Simula 67 → Smalltalk → Self        ML → Haskell → Rust
```

- **Algol W** (década de 1960) introduziu os registros (*records*)
  que temos em `algora` v3.
- **Simula 67** acrescentou classes, objetos e herança, para
  simulação.
- **Smalltalk** levou a ideia ao extremo: tudo é objeto, e a
  computação é troca de mensagens (como o _dispatcher_ da Aula 18).
- **Self** propôs objetos sem classes (protótipos). JavaScript herdou
  essa ideia.
- **ML** (e depois Haskell, OCaml, Rust) desenvolveu os tipos
  algébricos e o casamento de padrões.

O artigo clássico de Reddy (1988), citado na Aula 18, mostra
formalmente que objetos podem ser vistos como closures. Para ir além,
um texto muito recomendado é o de William Cook, *On Understanding
Data Abstraction, Revisited* (2009), que discute justamente a
diferença entre os dois caminhos que comparamos hoje.


## 8. Atualizando a tabela de síntese

Vamos acrescentar à tabela (`tabela-design.md`) o que aprendemos nesta
unidade. As células novas dizem respeito a **dados compostos**,
**encapsulamento** e **extensibilidade**:

| Linguagem   | Estado       | Dados compostos                        | Encapsulamento                 | Extensibilidade (problema da expressão) |
|-------------|--------------|----------------------------------------|--------------------------------|-----------------------------------------|
| `aljabr` v3 | —            | números + closures                     | — (não há dados a esconder)    | —                                       |
| `aljabr` v4 | —            | + valores etiquetados (soma + produto) | **nenhum**: estrutura sempre visível | nova **operação** fácil; nova **variante** difícil |
| `algora` v2 | store mutável| números + closures                     | variáveis capturadas (só closures) | —                                    |
| `algora` v3 | store mutável| + records (objetos)                    | escopo léxico, **por objeto**  | nova **variante** fácil; nova **operação** difícil |

Repare que `aljabr` v4 e `algora` v3 partem da **mesma** `aljabr`
v3 e variam **independentemente** nas dimensões *estado* e *dados*.
Nenhum dos dois é uma linguagem "funcional" ou "orientada a objetos"
por decreto: elas fazem escolhas específicas, e o que costumamos chamar
de paradigma é o conjunto dessas escolhas, e não um rótulo. Essa será
a tese da Unidade 9.


## Resumo (para guardar)

1. Um objeto em `algora` é um record cujos campos são closures (os
   métodos) que compartilham estado. Identidade, estado e
   comportamento vêm das regras que já tínhamos.
2. O estado pode ficar no record (público) ou em variável capturada
   (privado). A privacidade vem do **escopo léxico**, não de uma
   regra especial. Records nos dão **agregação**; closures nos dão
   **encapsulamento**.
3. A privacidade permite que o objeto garanta **invariantes** sobre o
   próprio estado.
4. `this`/`self` não são mágicos: em `algora` é uma variável comum
   (`obj`), e os métodos destacados continuam funcionando porque são
   closures.
5. Herança e polimorfismo podem ser obtidos como **padrões** (o
   construtor da subclasse reusa o da superclasse e sobrescreve campos).
   A **ligação tardia** é consequência da leitura de campo na hora da
   chamada. As linguagens oferecem construções para tornar isso
   conveniente e, às vezes, verificável.
6. Objetos e tipos algébricos organizam o mesmo conhecimento de
   formas opostas. O **problema da expressão** expressa o dilema: cada
   estilo facilita um tipo de evolução (nova variante × nova operação)
   e dificulta o outro.
7. Linguagens modernas oferecem os dois estilos.


## Para a próxima aula

Os erros que vimos nesta unidade (a leitura de um campo ausente, o
ramo `Pot` esquecido, `alimenta(5, 3)`; os dois últimos estão na seção
final) só aparecem **quando o programa executa**. Na Unidade 8, vamos
estudar sistemas de **tipos estáticos**: como detectar essa classe de
erros antes da execução? Começaremos pelo fragmento aritmética +
variáveis + funções de `aljabr` v3 (e voltaremos à decisão A da Aula
14: o que fazer com `2 + (1 < 2)`).


## Exercícios de fixação (sem necessidade de entrega)

1. **Invariante.** Escreva em `algora` v3 uma `Conta` com saldo
   **público** e mostre um programa que viola o invariante
   `saldo >= 0`. Depois, mostre que o mesmo programa não consegue
   violar o invariante na versão com saldo privado (a `Conta` da
   seção 2.5).

2. **Variantes e operações.** Acrescente a `Expr` (seção final, item B)
   a operação `profundidade` e a variante `Neg(a)` (negação unária),
   nos dois estilos. Conte, em cada estilo, **quantas definições
   existentes precisaram ser editadas** para cada mudança. O quadro da
   seção 6 se confirma?

3. **Herança.** Acrescente ao exemplo dos animais (seção 4) um
   `Passaro` cuja `voz` vale `4`. Como o `Passaro` reutiliza `fale` de
   `Animal`? Que parte do código de `Animal` **não** foi tocada? Faça
   o mesmo em `aljabr` v4 (seção 5) e compare o que precisou ser
   editado.

4. **Super.** No exemplo com energia (seção final, item C), o
   `Cachorro` guarda o `come` original em `comeBase` antes de
   sobrescrevê-lo. O que aconteceria se esquecêssemos a linha
   `var comeBase := obj.come;` e escrevêssemos
   `obj.come := fn (n) { obj.come(n * 2) };`? Rastreie a execução
   de `d.come(1)`.

5. **Método destacado.** Escreva em `algora` um programa em que dois
   objetos compartilham **a mesma closure** como método. O que cada
   um enxerga? Compare com o que ocorreria em JavaScript com `this`.

6. **Rastreamento.** Desenhe os ambientes e o store (como na figura
   da seção 1) depois de executar:

   ```text
   var animal := Animal(1);
   var cachorro := Cachorro(2);
   cachorro.fale()
   ```

   Quantas localizações do store guardam um nome (`nome_dado`, `nome`)?
   Em que ambientes estão? Qual `obj` o `fale` enxerga quando é
   chamado por `cachorro.fale()`?

7. **(Desafio)** Escreva em Python a `Expr` com `dataclass` (tipos
   algébricos) e uma função `profundidade` com `match`. Depois,
   tente acrescentar uma variante nova **sem editar** nenhuma função
   existente. Que recurso da linguagem (por exemplo,
   `functools.singledispatch`) ajuda? Que garantias você **perde**?

8. **(Desafio de design)** Proponha uma mudança em `algora` v3 que
   permitisse acrescentar operações a objetos já existentes sem
   editar seus construtores. Que regra de avaliação nova seria
   necessária? Que consequências ela teria para o encapsulamento?

---

**Leituras (opcionais)**

- REDDY, Uday S. *Objects as Closures: Abstract Semantics of Object
  Oriented Languages*, 1988 (já indicado na Aula 18).
- COOK, William R. *On Understanding Data Abstraction, Revisited*,
  2009.
- WADLER, Philip. *The Expression Problem*, 1998 (nota curta,
  disponível online).
