# Aula 19 — 23/Nov — Unidade 7 (3/3): closures × objetos, encapsulamento e o problema da expressão

> Tema da aula: fechar a Unidade 7 comparando os dois caminhos que
> abrimos na Aula 17 para modelar dados compostos: **tipos algébricos**
> (`aljabr` v4) e **objetos** (`algora` v3).
>
> Esta aula não introduz nenhuma construção nova de linguagem. Ela
> usa o que já temos (closures, estado mutável e records) para
> responder a três perguntas:
>
> 1. O que `algora` v3 realmente tem de "orientação a objetos"? E o
>    que não tem?
> 2. O que muda quando dados e operações ficam **juntos** (objetos)
>    ou **separados** (tipos algébricos)?
> 3. Que preço se paga em cada caso quando o programa **evolui**?
>
> Código completo dos exemplos: diretório [`exemplos/`](exemplos/).


## Retomando da aula anterior

Na Aula 18 vimos que um objeto pode ser construído a partir de três
ingredientes que já tínhamos estudado separadamente:

- **closures** com escopo léxico (Unidade 4);
- **estado com mutação**, graças à separação entre ambiente e store
  (Unidade 5);
- **records**, a única novidade de `algora` v3: `{ campo: exp }`,
  `obj.campo` e `obj.campo := exp`.

Percorremos uma progressão em três passos (closure sobre variável →
dispatcher de closures → record de closures) e deixamos, de
propósito, três itens em aberto. São eles que organizam o começo
desta aula:

1. Em um objeto, o estado fica **no record** (público) ou **numa
   variável capturada** (privado)? O que cada escolha dá ao
   programador?
2. O nome `obj` dentro do construtor faz o papel de `this` (Java) ou
   `self` (Python). Mas ele não tem regra semântica especial. O que
   isso muda?
3. Como ficaria a AST `Expr` da Aula 17 escrita em `algora`?

Como na aula passada, tudo o que mostramos usa apenas as regras que
já existem (a Aula 18 as introduz: criação de record, leitura e
escrita de campo). **Não há regra de avaliação nova nesta aula.** O
que há é uma tese: tudo o que chamamos de orientação a objetos
nesta aula já está implicado por essas regras.

> Uma observação sobre os exemplos. `algora` só tem números e
> closures (e records). Não temos strings nem listas. Por isso, onde
> um exemplo "real" imprimiria um texto, usaremos números como
> códigos (por exemplo, o som de um animal será `1` ou `2`) e
> operações como `tamanho()` em vez de `mostra()`.


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
c1.get() + c2.get()        // 3
```

> Código: [contador-privado.alg](exemplos/contador-privado.alg)

Compare com o ponto de partida da Unidade 7. Uma closure já agrupava
"código + dados capturados" (Unidade 4). O que o objeto acrescenta?

<details>
<summary>O que um objeto acrescenta a uma closure?</summary>

Três coisas, todas visíveis no exemplo acima:

1. **Múltiplos métodos** compartilhando o mesmo estado (`inc` e `get`
   enxergam o mesmo `n`). Uma closure isolada tem uma única
   operação, ou precisa do _dispatcher_ da Aula 18.
2. **Identidade explícita**: `c1` e `c2` são objetos distintos, cada
   um com seu `n`, e `var c3 := c1;` cria um segundo nome para o
   **mesmo** objeto.
3. **Mutação do estado interno**: as chamadas sucessivas observam as
   alterações das anteriores (é o store, e não o ambiente capturado,
   que muda).

O que não muda: o mecanismo de captura é o mesmo da Unidade 4. Um
método **é** uma closure. A diferença não está em uma construção
nova, mas em como combinamos as que já existiam.
</details>

A figura abaixo (simplificada) mostra o que existe depois de
`var c1 := Contador();`:

```text
        ambiente                      store

   c1 ────────────────> ℓ₁ ─────────> registro { inc ↦ closure₁,
                                                 get ↦ closure₂ }

   ambiente criado por Contador() (capturado por closure₁ e closure₂):
        n ────────────> ℓ₂ ─────────> 2
```

O record guarda **somente** os métodos. O valor de `n` vive em outra
localização, alcançável apenas pelas closures. Esse detalhe é o
centro da próxima seção.


## 2. Encapsulamento: duas representações do estado

Na Aula 18 vimos (variantes 3 e 3') que o estado de um objeto pode
ficar em dois lugares. Agora podemos compará-los com cuidado.

### 2.1 Estado privado: variável capturada

É o `Contador` da seção anterior. O estado é a variável local `n`.
Nenhum campo do record se chama `n`.

### 2.2 Estado público: campo do record

```text
def ContadorPublico() {
    var obj := { n: 0 };
    obj.inc := fn () { obj.n := obj.n + 1; obj.n };
    obj.get := fn () { obj.n };
    obj
}
```

> Código: [contador-publico.alg](exemplos/contador-publico.alg)

Compare o que acontece em cada versão:

| Experimento                 | `Contador` (privado)            | `ContadorPublico`               |
|-----------------------------|---------------------------------|---------------------------------|
| `c.get()` após dois `inc()` | `2`                             | `2`                             |
| ler `c.n`                   | `erro` (o record não tem `n`)   | `2`                             |
| `c.n := 100; c.get()`       | `2` (!)                         | `100`                           |

A última linha da coluna da esquerda merece atenção. A escrita
`c.n := 100` não é um erro: atribuir a um campo que não existe o
**cria** (é exatamente o que fazemos com `obj.inc := fn …` sobre um
record vazio). Mas o campo novo não tem relação alguma com a variável
`n` capturada pelas closures. O estado interno continua intacto.

> **Pergunta:** não há regra nenhuma de "campo privado" nas regras de
> `algora`. De onde vem, então, a privacidade de `n`?
> <details>
> <summary>Clique para ver a resposta</summary>
>
> <br>Do **escopo léxico**. A variável `n` só existe no ambiente
> criado pela chamada a `Contador()`, e só as closures criadas lá
> dentro o capturaram. Nenhuma expressão do programa que esteja fora
> do corpo de `Contador` pode nomear essa variável. Não é um
> mecanismo a mais: é a consequência de uma decisão que tomamos na
> Unidade 4.
> </details>

### 2.3 Por que isso importa: invariantes

Privacidade não é só estética. Ela permite que o objeto **garanta
propriedades** sobre o próprio estado. Considere uma conta bancária
cujo saldo nunca deve ficar negativo:

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

> Código: [conta-invariante.alg](exemplos/conta-invariante.alg)

Como o saldo só pode ser alterado por `deposita` e `saca`, e ambos
preservam a propriedade `saldo >= 0` (supondo `inicial >= 0`), **todo
programa** que usa uma `Conta` mantém essa propriedade. Essa propriedade
é chamada de _invariante_ do objeto.

> **Pergunta:** o que acontece com o invariante se escrevermos a
> `Conta` com o saldo em um campo público (`obj.saldo := inicial`)?
> <details>
> <summary>Clique para ver a resposta</summary>
>
> <br>Ele deixa de valer: qualquer trecho do programa pode executar
> `c.saldo := -1000`. O invariante deixa de ser uma propriedade da
> **conta** e passa a ser uma promessa de **todos os usuários**
> da conta. É a mesma diferença entre confiar numa interface e
> confiar em uma convenção.
> </details>

Guarde essa observação. Ela volta no Interlúdio (Aula 28), quando
formos além de _nomear_ uma interface e perguntarmos como _especificar_
o que ela promete (contratos, invariantes).

### 2.4 Agregar não é encapsular

Duas ideias costumam ser confundidas:

- **Agregação**: reunir dados e operações num mesmo lugar (o record
  com campos e métodos). `ContadorPublico` tem isso.
- **Encapsulamento** (*information hiding*): **esconder** a
  representação, de modo que só a interface seja acessível.
  `Contador` tem isso.

Em `algora`, o programador escolhe entre as duas representações. Nas
linguagens convencionais, essa escolha é feita por palavras como
`private`.

### 2.5 Como as linguagens reais tratam isso

| Linguagem  | Como se esconde o estado                                                                 |
|------------|------------------------------------------------------------------------------------------|
| Java       | `private`, **imposto pelo compilador**; vale por **classe** (outra instância da mesma classe pode acessar) |
| Python     | convenção `_campo` (o interpretador não impede o acesso)                                 |
| JavaScript | campos `#privado` (versões recentes) ou, historicamente, closures, como em `algora`       |
| `algora`   | escopo léxico: a variável simplesmente não é nomeável de fora; vale por **objeto**       |

Repare na diferença sutil entre Java e `algora`: em Java, o código da
classe `Conta` pode ler `outra.saldo` de **outra** conta; em
`algora`, cada objeto tem seu próprio ambiente capturado, e a
privacidade é **por objeto**.


## 3. `this` e `self`: um nome comum

Na Aula 18 chamamos a atenção para o fato de que o nome `obj` é uma
variável como outra qualquer. Agora que temos o escopo léxico bem
estabelecido, dá para entender o que isso significa por comparação:

| | Java | Python | JavaScript | `algora` v3 |
|---|---|---|---|---|
| Nome do "objeto atual" | `this` | `self` | `this` | `obj` (qualquer nome) |
| É palavra reservada? | sim | não (convenção; é o 1º parâmetro) | sim | não |
| Quem define seu valor? | o compilador, na chamada `o.m()` | o mecanismo de métodos ligados: `o.m(x)` equivale a `C.m(o, x)` | depende de **como** a função é chamada | o escopo léxico: a variável capturada na criação |

O caso de JavaScript é revelador. Nas funções comuns, o `this` não é
determinado pelo **lugar onde a função foi escrita**, mas por **como**
foi chamada. Em termos da Unidade 4, é um comportamento mais próximo
de escopo **dinâmico** do que de léxico.

Em `algora`, como `obj` é uma variável capturada, o método sempre
"lembra" de qual objeto é. Experimente:

```text
var c := Contador();
var f := c.inc;        // pega o método, sem o objeto
f();                   // 1
f();                   // 2
c.get()                // 2
```

> Código: [metodo-destacado.alg](exemplos/metodo-destacado.alg)

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


## 4. Herança e polimorfismo: padrões, não construções

Herança e polimorfismo são, junto com encapsulamento, as ideias
associadas à OO. Será que `algora` v3 precisa de novas construções
para expressá-las? Vamos tentar sem nenhuma.

### 4.1 O problema

Queremos um tipo `Animal` com estado (energia), a operação `come` e a
operação `fala`. Dois especializados: `Gato` (fala `1`) e `Cachorro`
(fala `2`, e come em dobro). Além disso, queremos a operação `reage(n)`
("come `n` e depois fala") escrita **uma única vez**, no `Animal`.

### 4.2 Decisão de design

Em vez de uma construção `class … extends …`, adotamos um padrão:

- o "construtor" do tipo geral **recebe o record** a ser equipado,
  em vez de criar um novo;
- o construtor do tipo específico cria o record, chama o construtor
  geral sobre ele e depois **sobrescreve** os campos desejados.

### 4.3 Código

```text
def Animal(obj) {
    var energia := 10;                          // estado privado
    obj.come    := fn (n) { energia := energia + n; energia };
    obj.energia := fn () { energia };
    obj.fala    := fn () { 0 };                 // 0: silêncio
    obj.reage   := fn (n) { obj.come(n); obj.fala() };
    obj
}

def Gato() {
    var obj := {};
    Animal(obj);
    obj.fala := fn () { 1 };                    // 1: miau
    obj
}

def Cachorro() {
    var obj := {};
    Animal(obj);
    var comeBase := obj.come;                   // guarda o método original ("super")
    obj.come := fn (n) { comeBase(n * 2) };     // come em dobro
    obj.fala := fn () { 2 };                    // 2: au
    obj
}
```

> Código: [animais-oo.alg](exemplos/animais-oo.alg)

```text
var g := Gato();
var d := Cachorro();

g.reage(5);        // energia: 15; devolve 1
d.reage(5);        // come(5), mas o come do Cachorro dobra: energia 20; devolve 2
d.energia()        // 20
```

Observe com atenção o que aconteceu em `d.reage(5)`:

1. `reage` foi definido dentro de `Animal`, mas chama `obj.come(n)` e
   `obj.fala()`.
2. Como `obj` é o **mesmo record** que `Cachorro` equipou (e
   modificou), a leitura do campo `come` encontra a versão do
   `Cachorro`. Por isso a energia sobe 10, e não 5.

A escolha do método a executar é feita **na hora da chamada**, pela
leitura do campo. Isso é o que as linguagens chamam de _ligação
tardia_ (*late binding*) ou despacho dinâmico, e aqui ele é uma
consequência da regra de leitura de campo, não uma regra à parte.

### 4.4 Polimorfismo

```text
def alimenta(a, n) { a.reage(n) }

alimenta(g, 3);    // 1
alimenta(d, 3)     // 2
```

A função `alimenta` não sabe nem precisa saber se recebeu um `Gato`
ou um `Cachorro`. Ela só exige que o argumento tenha um campo `reage`
que seja uma função de um parâmetro. É o chamado _duck typing_
(familiar em Python). Esse é o polimorfismo que `algora` oferece: o
**mesmo** trecho de código se comporta de formas diferentes conforme o
objeto recebido.

> **Pergunta:** e o que acontece com `alimenta(5, 3)`?
> <details>
> <summary>Clique para ver a resposta</summary>
>
> <br>Um `erro` em tempo de execução: `5` não é um record, logo não
> há campo `reage` a ser lido. Em `algora` nada verifica, antes de
> executar, que `alimenta` recebe "algo com `reage`". É uma
> propriedade da tipagem dinâmica, que será tema da Unidade 8.
> </details>

### 4.5 O que `algora` v3 **não** oferece

O padrão acima mostra que **dá para fazer** herança e polimorfismo.
Mas é bom notar o que fica por conta do programador:

- não há verificação de que `Gato` e `Cachorro` "são" `Animal` (nenhuma
  relação é declarada, só um costume de chamar `Animal(obj)`);
- `super` é só uma variável que guardamos (`comeBase`);
- não há herança de classes: cada instância copia os métodos para o
  seu próprio record;
- não há como perguntar a um objeto de qual "tipo" ele é.

Linguagens como Java e Python adicionam construções (`class`,
`extends`, `super`) justamente para tornar esse padrão mais
conveniente, mais legível e, em Java, verificável pelo compilador.
Uma linguagem como JavaScript (e a linguagem Self, que a inspirou)
preferiu outro caminho: **objetos sem classes**, em que um objeto
delega a outro objeto (_protótipo_). Nosso estilo está bem mais
próximo desse segundo caminho.


## 5. O outro caminho: o mesmo problema com tipos algébricos

Vamos modelar os mesmos animais em `aljabr` v4 (Aula 17). Lá não há
estado mutável nem métodos. Dados e operações ficam **separados**:

```text
type Animal = Gato(e) | Cachorro(e)

let fala = fn (a) =>
    match a { Gato(_) => 1  Cachorro(_) => 2 }
in
let come = fn (a, n) =>
    match a {
        Gato(e)     => Gato(e + n)
        Cachorro(e) => Cachorro(e + 2 * n)
    }
in
let reage = fn (a, n) => fala(come(a, n)) in
reage(Cachorro(10), 5)                                  // 2
```

> Código: [animais-adt.alj](exemplos/animais-adt.alj)

Compare as duas versões:

| | Objetos (`algora`) | Tipos algébricos (`aljabr` v4) |
|---|---|---|
| Onde estão as operações | **dentro** de cada animal (campos do record) | **fora**, em funções com `match` |
| Como se escolhe a operação | pela leitura do campo no objeto (ligação tardia) | inspecionando a **forma** do valor (`match`) |
| Estado | mutável: `come` altera o animal | imutável: `come` devolve um **novo** animal |
| Representação | escondida (privada), se quisermos | sempre visível: qualquer função pode usar `match` |
| Variantes | abertas: qualquer um pode criar um novo "tipo" de animal | fechadas: listadas no `type` |

> **Pergunta:** `come(Cachorro(10), 5)` em `aljabr` v4 vale
> `Cachorro(20)`. Em `algora`, `d.come(5)` devolve `20`, mas o que
> **mudou**?
> <details>
> <summary>Clique para ver a resposta</summary>
>
> <br>Em `algora`, o **conteúdo de uma localização do store** mudou
> (`energia` agora vale 20). Em `aljabr` v4 nada mudou: foi criado um
> valor novo, e o antigo `Cachorro(10)` continua existindo,
> intacto. É a diferença entre mutação e transparência referencial
> (Aula 15) aparecendo na modelagem de dados.
> </details>

Uma observação de vocabulário, para evitar confusão. Chamamos os
tipos de `aljabr` v4 de **tipos algébricos de dados** (soma e produto).
Isso **não** é o mesmo que **tipo abstrato de dados** (que esconde a
representação atrás de uma interface, como o `Contador`). Em inglês, as
siglas são diferentes (*ADT* para algébrico, *ADT* também para
abstrato, infelizmente), e a literatura às vezes mistura os dois. Nesta
disciplina, usamos "tipo algébrico" para o primeiro e "encapsulamento"
para a ideia do segundo.


## 6. O problema da expressão

Os dois caminhos parecem resolver problemas semelhantes. Há alguma
diferença **prática** entre eles? Há, e ela aparece quando o programa
**evolui**. Vamos ver com a AST de expressões que usamos desde a
Unidade 2.

### 6.1 A AST escrita nos dois estilos

**Tipos algébricos (`aljabr` v4).** Duas operações, `avalia` e
`tamanho` (o número de nós da árvore), escritas como funções que
fazem `match`:

```text
type Expr = Num(n) | Add(a, b) | Mul(a, b)

letrec avalia = fn (e) =>
    match e {
        Num(n)    => n
        Add(a, b) => avalia(a) + avalia(b)
        Mul(a, b) => avalia(a) * avalia(b)
    }
in
letrec tamanho = fn (e) =>
    match e {
        Num(_)    => 1
        Add(a, b) => 1 + tamanho(a) + tamanho(b)
        Mul(a, b) => 1 + tamanho(a) + tamanho(b)
    }
in
avalia(Mul(Add(Num(2), Num(3)), Num(4)))                // 20
```

> Código: [expr-adt.alj](exemplos/expr-adt.alj)

**Objetos (`algora` v3).** Cada nó é um objeto que sabe se avaliar e
dizer seu tamanho:

```text
def Num(n) {
    var obj := {};
    obj.avalia  := fn () { n };
    obj.tamanho := fn () { 1 };
    obj
}

def Add(a, b) {
    var obj := {};
    obj.avalia  := fn () { a.avalia() + b.avalia() };
    obj.tamanho := fn () { 1 + a.tamanho() + b.tamanho() };
    obj
}

def Mul(a, b) {
    var obj := {};
    obj.avalia  := fn () { a.avalia() * b.avalia() };
    obj.tamanho := fn () { 1 + a.tamanho() + b.tamanho() };
    obj
}

var e := Mul(Add(Num(2), Num(3)), Num(4));
e.avalia();                                             // 20
e.tamanho()                                             // 5
```

> Código: [expr-oo.alg](exemplos/expr-oo.alg)

Observe que são duas organizações do **mesmo** conhecimento. Podemos
ver os dados como uma tabela, em que as linhas são as variantes
(`Num`, `Add`, `Mul`) e as colunas são as operações (`avalia`,
`tamanho`):

|         | `avalia`        | `tamanho`        |
|---------|-----------------|------------------|
| `Num`   | `n`             | `1`              |
| `Add`   | soma            | `1 + …`          |
| `Mul`   | produto         | `1 + …`          |

- Em **objetos**, o programa é organizado **por linhas**: cada
  variante agrupa tudo o que sabe fazer.
- Em **tipos algébricos**, o programa é organizado **por colunas**:
  cada operação agrupa o que faz com cada variante.

### 6.2 Evoluindo o programa: uma variante nova

Queremos agora a potenciação, `Pot(a, b)`.

**Em `algora` v3**, basta **um construtor novo**. Nenhum código
existente é tocado:

```text
def Pot(a, b) {
    var obj := {};
    obj.avalia  := fn () { a.avalia() ** b.avalia() };
    obj.tamanho := fn () { 1 + a.tamanho() + b.tamanho() };
    obj
}

var p := Add(Pot(Num(2), Num(3)), Num(1));
p.avalia()                                              // 9
```

> Código: [expr-pot-oo.alg](exemplos/expr-pot-oo.alg)

Repare que `Add` aceita um `Pot` sem saber que ele existe. É o
polimorfismo da seção 4 trabalhando a nosso favor.

**Em `aljabr` v4**, é preciso **editar** o `type` e **todas** as funções
com `match`:

```text
type Expr = Num(n) | Add(a, b) | Mul(a, b) | Pot(a, b)      // editado

letrec avalia = fn (e) =>
    match e {
        Num(n)    => n
        Add(a, b) => avalia(a) + avalia(b)
        Mul(a, b) => avalia(a) * avalia(b)
        Pot(a, b) => avalia(a) ** avalia(b)                  // novo ramo
    }
in
letrec tamanho = fn (e) =>
    match e {
        Num(_)    => 1
        Add(a, b) => 1 + tamanho(a) + tamanho(b)
        Mul(a, b) => 1 + tamanho(a) + tamanho(b)
        Pot(a, b) => 1 + tamanho(a) + tamanho(b)             // novo ramo
    }
in
avalia(Add(Pot(Num(2), Num(3)), Num(1)))                // 9
```

> Código: [expr-pot-adt.alj](exemplos/expr-pot-adt.alj)

> **Pergunta:** o que acontece se esquecermos o ramo `Pot` em
> `tamanho`?
> <details>
> <summary>Clique para ver a resposta</summary>
>
> <br>`tamanho(Pot(...))` vale `erro`, pela regra (MatchNenhum) da
> Aula 17. Só descobrimos ao executar. Em linguagens como Rust e
> Haskell, o compilador recusa o programa antes (verificação de
> exaustividade). Em `aljabr` v4, essa verificação não existe, pois
> não temos tipos estáticos (ainda).
> </details>

### 6.3 Evoluindo o programa: uma operação nova

Agora queremos uma nova operação, `profundidade` (a altura da árvore).

**Em `aljabr` v4**, basta **uma função nova**. Nenhum código existente
é tocado:

```text
letrec profundidade = fn (e) =>
    match e {
        Num(_)    => 1
        Add(a, b) => 1 + (if profundidade(a) < profundidade(b)
                          then profundidade(b) else profundidade(a))
        Mul(a, b) => 1 + (if profundidade(a) < profundidade(b)
                          then profundidade(b) else profundidade(a))
    }
in
profundidade(Mul(Add(Num(2), Num(3)), Num(4)))          // 3
```

> Código: [expr-prof-adt.alj](exemplos/expr-prof-adt.alj)

**Em `algora` v3**, é preciso **editar todos os construtores**
(`Num`, `Add`, `Mul`, e `Pot` se já existir), acrescentando
`obj.profundidade := …` a cada um:

> Código: [expr-prof-oo.alg](exemplos/expr-prof-oo.alg)

### 6.4 O quadro geral

|                            | Objetos (`algora`)              | Tipos algébricos (`aljabr` v4)       |
|----------------------------|---------------------------------|--------------------------------------|
| **Nova variante** (`Pot`)  | **fácil**: um construtor novo   | **difícil**: editar `type` e todos os `match` |
| **Nova operação** (`profundidade`) | **difícil**: editar todos os construtores | **fácil**: uma função nova    |

Este dilema é conhecido como o **problema da expressão** (*expression
problem*), nome dado por Philip Wadler em 1998. Cada estilo é
**fechado** em uma dimensão e **aberto** na outra. O dilema completo
exige ainda que a extensão seja feita **sem alterar o código
existente** e **sem perder a verificação de tipos** (na formulação
original, estática). Esse último requisito só fará pleno sentido
depois da Unidade 8, onde voltaremos ao problema.

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

### 6.5 Soluções reais (apenas menção)

Muitas linguagens tentam equilibrar os dois lados. Sem entrar em
detalhes:

- o padrão de projeto _Visitor_ (Java e outras) simula "nova operação
  fácil" em um estilo orientado a objetos, ao custo de tornar "nova
  variante" mais trabalhosa;
- _traits_ (Rust, Scala), _type classes_ (Haskell) e _protocols_
  (Swift) permitem associar operações novas a tipos existentes, sem
  editar sua definição;
- Python oferece soluções parciais (`functools.singledispatch`,
  protocolos, *mixins* e até *monkey patching*), mas sem verificação
  estática;
- as interfaces de Java resolvem apenas parte do problema.

Esse é um dos motivos pelos quais as linguagens modernas misturam os
dois caminhos (Seção 7).

### 6.6 O mesmo em Python

Python permite os dois estilos. Em Python, o estilo de objetos fica
assim (compare com `expr-oo.alg`):

```python
class Num:
    def __init__(self, n):
        self.n = n
    def avalia(self):
        return self.n
    def tamanho(self):
        return 1

class Add:
    def __init__(self, a, b):
        self.a, self.b = a, b
    def avalia(self):
        return self.a.avalia() + self.b.avalia()
    def tamanho(self):
        return 1 + self.a.tamanho() + self.b.tamanho()
```

> Código completo, nos dois estilos: [expr.py](exemplos/expr.py)

E o estilo de tipos algébricos é o da Aula 17 (`dataclass` + `match`).
Os dois convivem na mesma linguagem, e é o programador quem escolhe.
A escolha tem as mesmas consequências que vimos acima.


## 7. Comparando com linguagens reais

Com o que construímos, vale posicionar `algora` v3 e `aljabr` v4
diante de linguagens que conhecemos.

| | `algora` v3 | Java | Python | JavaScript | Rust |
|---|---|---|---|---|---|
| Objetos | records de closures | instâncias de classes | instâncias de classes (guardam campos em um dicionário, `__dict__`) | objetos com protótipos | `struct` + `impl` |
| Classes | padrão de projeto (função construtora) | obrigatórias | são valores (objetos) | `class` é açúcar sobre protótipos | não há |
| Objeto atual | variável comum | `this` | `self` | `this` | `self` |
| Estado privado | escopo léxico | `private` (por classe) | convenção `_x` | `#campo` | por módulo |
| Herança | padrão (copiar e sobrescrever) | de classes (simples) + interfaces | de classes (múltipla) | por protótipos/`class` | **não há**; usa-se `trait` |
| Tipos algébricos | via `aljabr` v4 | `sealed` + `record` + `switch` com padrões (versões recentes) | `dataclass` + `match` | convenções | `enum` + `match` (nativos) |

Observe o padrão geral: as linguagens **modernas** tendem a oferecer
**os dois** caminhos. Java foi acrescentando suporte a tipos
algébricos; Python também; Rust evitou herança e põe os tipos
algébricos no centro. Isso é um sinal de que ambos os estilos têm
vantagens reais, e de que o problema da expressão não tem solução
única.

### Um pouco de história

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
de paradigma é o conjunto dessas escolhas. Essa será a tese da
Unidade 9.


## Resumo (para guardar)

1. Um objeto em `algora` é um record cujos campos são closures (os
   métodos) que compartilham estado. Identidade, estado e
   comportamento vêm das regras que já tínhamos.
2. O estado pode ficar no record (público) ou em variável capturada
   (privado). A privacidade vem do **escopo léxico**, não de uma
   regra especial.
3. A privacidade permite que o objeto garanta **invariantes** sobre o
   próprio estado.
4. `this`/`self` não são mágicos: em `algora` é uma variável comum, e
   a ligação tardia é consequência da leitura de campo na hora da
   chamada.
5. Herança e polimorfismo podem ser obtidos como **padrões** (copiar e
   sobrescrever; chamar campos). As linguagens oferecem construções
   para tornar isso conveniente e, às vezes, verificável.
6. Objetos e tipos algébricos organizam o mesmo conhecimento de
   formas opostas (por linhas ou por colunas). O **problema da
   expressão** expressa o dilema: cada estilo facilita um tipo de
   evolução e dificulta o outro.
7. Linguagens modernas oferecem os dois estilos.


## Para a próxima aula

Em todos os exemplos de hoje, os erros que vimos (`alimenta(5, 3)`, o
ramo `Pot` esquecido, a leitura de um campo ausente) só aparecem
**quando o programa executa**. Na Unidade 8, vamos estudar sistemas de
**tipos estáticos**: como detectar essa classe de erros antes da
execução? Começaremos pelo fragmento aritmética + variáveis + funções
de `aljabr` v3 (e voltaremos à decisão A da Aula 14: o que fazer com
`2 + (1 < 2)`).


## Exercícios de fixação (sem necessidade de entrega)

1. **Invariante.** Escreva em `algora` v3 uma `Conta` com saldo
   **público** e mostre um programa que viola o invariante
   `saldo >= 0`. Depois, mostre que o mesmo programa não consegue
   violar o invariante na versão com saldo privado.

2. **Variantes e operações.** Acrescente a `Expr` a operação
   `profundidade` e a variante `Neg(a)` (negação unária), nos dois
   estilos. Conte, em cada estilo, **quantas definições existentes
   precisaram ser editadas** para cada mudança. O quadro da seção 6.4
   se confirma?

3. **Herança.** Acrescente ao exemplo dos animais um `Passaro` cuja
   `fala` vale `3` e que come a metade (use `n / 2`). Como o
   `Passaro` reutiliza `reage` de `Animal`? Que parte do código do
   `Animal` **não** foi tocada?

4. **Super.** No `Cachorro`, o que aconteceria se esquecêssemos a
   linha `var comeBase := obj.come;` e escrevêssemos
   `obj.come := fn (n) { obj.come(n * 2) };`? Rastreie a execução
   de `d.come(1)`.

5. **Método destacado.** Escreva em `algora` um programa em que dois
   objetos compartilham **a mesma closure** como método. O que cada
   um enxerga? Compare com o que ocorreria em JavaScript com `this`.

6. **Rastreamento.** Desenhe os ambientes e o store (como na figura
   da seção 1) depois de executar:

   ```text
   var g := Gato();
   var d := Cachorro();
   d.reage(5)
   ```

   Quantos "`energia`" existem no store? Onde está cada um?

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
