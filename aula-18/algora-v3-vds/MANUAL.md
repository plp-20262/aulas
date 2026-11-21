# Manual de Algora (v3)

**Algora** é uma pequena linguagem que mistura duas ideias:

- do lado funcional (herdado de Aljabr): funções são valores, podem ser anônimas e capturam o ambiente onde foram criadas (*closures*);
- do lado imperativo (inspirado em Algol): variáveis mutáveis, atribuição com `:=` e programas escritos como sequência de comandos.

Há ainda um toque de Rust: **tudo que termina com uma expressão devolve o valor dela**. Não existe `return`.

A v3 acrescenta **records** e, com eles, **objetos**: literais `{ nome: exp, ... }`, acesso a campo `e.n` e atribuição a campo `e.n := v`. Não há `class`, nem `new`, nem açúcar para métodos, nem palavra reservada `this` (você pode usar qualquer identificador — `this`, `self`, `obj`, `me` — para nomear o record corrente; é convenção, não feature).

Este manual mostra como usar a linguagem. Para as regras formais (gramática e semântica operacional), consulte o `README.md`.

## 1. Primeiro programa

Um programa é uma lista de comandos terminados em `;`, seguida de **uma expressão final** (sem `;`). O valor dessa expressão é o resultado do programa.

```
var x := 10;
var y := 20;
x + y
```

Resultado: `30`.

> Todo programa precisa ter a expressão final. Um programa que termina em `;` é um erro de sintaxe.

Algora não tem comentários.

## 2. Valores e operadores

Os valores são **números** e **funções** (e, na v3, **records**). Os literais são inteiros (`0`, `42`), mas o tipo numérico é o dos reais, então `/` pode produzir resultados fracionários.

| Operador | Significado | Observação |
|---|---|---|
| `**` | potência | associa à direita: `2 ** 3 ** 2` é `2 ** 9` |
| `+x`, `-x` | sinal unário | apenas um sinal por vez |
| `*`, `/` | multiplicação, divisão | |
| `+`, `-` | soma, subtração | |
| `==`, `<` | comparação | no máximo uma por expressão |

A tabela vai da maior para a menor precedência. Parênteses mudam a ordem como de costume.

Detalhes que costumam surpreender:

- O sinal unário tem precedência **maior** que `**`: `-2 ** 2` vale `(-2) ** 2 = 4`.
- Não é possível encadear comparações: `a < b < c` não é válido.
- Não há `and`, `or` nem `not`. Use `if` para combinar condições.

**Verdadeiro e falso** são números: `0` é falso e qualquer outro número é verdadeiro. Por isso `if` aceita qualquer número como condição, e usar uma função como condição é um erro.

## 3. Variáveis

`var` declara uma variável nova, com valor inicial obrigatório. `:=` altera uma variável já declarada.

```
var contador := 0;
contador := contador + 1;
contador := contador * 10;
contador
```

Resultado: `10`.

Duas coisas para lembrar:

- Tanto a declaração quanto a atribuição são **comandos**, não expressões. Não dá para escrever `1 + (x := 2)`.
- Atribuir a um nome que não foi declarado é erro. Usar um nome não declarado também.

Os dois usos de `:=` parecem iguais, mas fazem coisas diferentes: `var x := e` cria uma variável (escondendo qualquer `x` anterior), enquanto `x := e` altera a que já existe.

## 4. Blocos e escopo

Um bloco `{ ... }` tem a mesma forma de um programa: zero ou mais comandos e uma expressão final. O bloco **vale o valor da expressão final** e pode aparecer onde uma expressão é esperada.

```
var y := {
  var t := 3;
  t * t
};
y + 1
```

Resultado: `10`. A variável `t` só existe dentro do bloco.

Variáveis declaradas dentro do bloco **escondem** as de fora com o mesmo nome. Já a atribuição, sem `var`, altera a variável existente, esteja onde estiver:

```
var a := 1;
var b := 1;
{ var a := 10; b := 20; a };
a + b
```

Resultado: `21`. O `a` de fora continua `1` (o de dentro era outra variável), mas `b` foi alterado.

> **Bloco × record.** Em posição de expressão, `{ ... }` pode ser um bloco ou um record literal. A distinção é pelo conteúdo: `{ }` é o record vazio; `{ nome: ... }` é um record; qualquer outra coisa (`{ var ...`, `{ x ; ...`, `{ x + 1 }`, ...) é um bloco. Veja a §9.

## 5. Condicional

`if` é uma **expressão**: devolve o valor do bloco escolhido. O `else` é obrigatório e as duas ramificações são blocos.

```
var n := 7;
var tipo := if n < 10 { 1 } else { 2 };
tipo
```

Resultado: `1`.

Se um `if` for usado como comando (só pelos efeitos), ele precisa terminar com `;` como qualquer expressão-comando:

```
var m := 0;
if n == 7 { m := 1; 0 } else { 0 };
m
```

Resultado: `1`.

## 6. Funções

### Funções anônimas: `fn`

```
var dobro := fn(x) { x * 2 };
dobro(21)
```

Resultado: `42`.

### Funções nomeadas: `def`

`def` declara uma função e pode chamar a si mesma, o que dá **recursão**. Como `def` é um comando que termina em bloco, não leva `;`.

```
def fat(n) {
  if n < 2 { 1 } else { n * fat(n - 1) }
}
fat(5)
```

Resultado: `120`.

Notas:

- Laços são feitos com `while` (veja a §7).
- Funções são valores comuns: podem ser passadas como argumento, devolvidas e guardadas em variáveis.
- Chamadas encadeiam: `f(1)(2)` chama `f(1)` e aplica o resultado a `2`.
- Os argumentos são avaliados da esquerda para a direita e passados **por valor**. Os parâmetros são variáveis locais, então atribuir a um parâmetro não afeta o chamador.
- Chamar algo que não é função, ou passar o número errado de argumentos, é erro.

```
def duas_vezes(f, x) { f(f(x)) }
duas_vezes(fn(n) { n * 2 }, 5)
```

Resultado: `20`.

> Para recursão, use `def`. Com `var f := fn(n) { ... f(n - 1) ... }`, o nome `f` ainda não existe quando a função é criada, então a chamada recursiva falha.

## 7. Laços com `while`

O comando `while` repete um corpo de comandos enquanto a condição for verdadeira (`0` é falso, qualquer outro número é verdadeiro).

```
var i := 0;
var soma := 0;
while i < 5 {
    soma := soma + i;
    i := i + 1;
}
soma
```

Resultado: `10`.

Regras importantes:

- O corpo é um bloco de comandos, **sem expressão final**. Cada expressão dentro do corpo precisa terminar com `;` (é um `exp ;`).
- O `while` é um comando e **não leva `;`** depois do `}` que fecha o corpo. O próximo comando ou a expressão final do programa começa diretamente a seguir.
- O `while` não produz valor: não pode ser a última coisa do programa nem aparecer onde se espera uma expressão (por exemplo, `var x := while ...` é inválido).
- A condição é numérica, como em `if`. Usar uma função como condição de `while` é erro.

## 8. Closures e estado

Uma função **lembra das variáveis do lugar onde foi criada**, e não apenas dos valores que elas tinham: se a variável mudar, a função enxerga a mudança, e se a função a alterar, quem está de fora também enxerga.

```
var total := 0;
def soma_ate(n) {
  if n == 0 { 0 } else { total := total + n; soma_ate(n - 1) }
}
soma_ate(4);
total
```

Resultado: `10`.

Isso permite criar funções com estado privado, como um contador:

```
def faz_contador() {
  var n := 0;
  fn() { n := n + 1; n }
}
var c := faz_contador();
c();
c();
c()
```

Resultado: `3`. Cada chamada a `faz_contador()` cria um `n` novo, e portanto um contador independente.

## 9. Records e objetos

### 9.1 Criando records

Um record é um mapa de nomes para valores. O literal é `{ nome: exp, ... }`:

```
var p := { x: 0, y: 0 };
p.x + p.y
```

Resultado: `0`.

O record vazio é `{}` — o idioma para começar um objeto:

```
var obj := {};
```

### 9.2 Acesso e atribuição a campos

`e.n` lê o campo `n` do record denotado por `e`. `e.n := v` escreve no campo (usa `:=`, como atribuição de variável):

```
var p := { x: 0 };
p.x := 10;
p.x
```

Resultado: `10`.

Atribuir a um campo inexistente **cria** o campo:

```
var p := {};
p.z := 42;
p.z
```

Resultado: `42`.

### 9.3 Aliasing

Records são mutáveis e **aliased**: atribuir um record a outra variável copia a localização, não o mapa:

```
var p := { x: 1 };
var q := p;
q.x := 99;
p.x
```

Resultado: `99`.

### 9.4 Métodos são campos com closures

Não há sintaxe especial para métodos. Um método é apenas um campo que contém uma função:

```
var obj := {};
obj.n := 0;
obj.inc := fn () { obj.n := obj.n + 1; obj.n };
obj.inc();
obj.inc();
obj.n
```

Resultado: `2`.

### 9.5 Convenção: como nomear o record corrente?

Não há palavra reservada `this` em Algora. A convenção (como em Python, onde `self` também é só convenção) é o programador escolher um nome — geralmente `this`, `self` ou `obj` — e usá-lo como qualquer outra variável. Closures capturam esse nome lexicalmente:

```
def Contador() {
  var this := {};                                 // 'this' aqui é só um nome escolhido pelo programador
  this.n := 0;
  this.inc := fn () { this.n := this.n + 1; this.n };
  this
}
var c := Contador();
c.inc();
c.inc();
c.n
```

Resultado: `2`.

O mesmo código com `self` no lugar de `this` funciona igual:

```
def Contador() {
  var self := {};
  self.n := 0;
  self.inc := fn () { self.n := self.n + 1; self.n };
  self
}
```

Cada chamada a `Contador()` cria um `self`/`this` novo (um record novo), então contadores são independentes:

```
var c1 := Contador();
var c2 := Contador();
c1.inc();
c2.inc();
c2.inc();
c1.n + c2.n
```

Resultado: `3`.

> **A captura é lexical.** Se você extrair um método para uma variável (`var f := obj.inc`), a função continua vendo o `this`/`self` do lugar onde foi criada, não o `obj` do qual foi extraída. Não há rebinding implícito — porque não há keyword `this` para rebindar.

### 9.6 Chamada de método

`obj.m(args)` é equivalente a `(obj.m)(args)`: lê o campo `m` (que deve conter uma função) e aplica aos argumentos. Não há despacho especial.

```
var obj := {};
obj.n := 0;
obj.inc := fn () { obj.n := obj.n + 1; obj.n };
obj.inc();    // equivalente a (obj.inc)()
```

### 9.7 Record como valor de retorno

O corpo de uma função é um bloco-expressão. Para retornar um record, use chaves duplas (o `{` externo é o bloco, o interno é o record):

```
def ponto(x, y) { { x: x, y: y } }
var p := ponto(3, 4);
p.x + p.y
```

Resultado: `7`.

### 9.8 Sem `class`, sem `new`

Algora v3 não tem `class`, `new`, nem açúcar para métodos. O construtor é uma função que cria o record, equipa e devolve (como `Contador()` acima). A noção de `class` como açúcar de AST é uma evolução futura, não desta versão.

### 9.9 Adição dinâmica de campos

Campos podem ser adicionados a qualquer momento:

```
var p := { x: 1 };
p.y := 2;
p.x + p.y
```

Resultado: `3`.

### 9.10 `{}` como record vazio

Em posição de expressão, `{}` é o record vazio. Em posição de comando (corpo de `while`), `{}` é um bloco de comando vazio. Exemplos:

```
var vazio := {};          // record vazio
while 0 { }               // corpo de comando vazio (não executa)
```

### 9.11 Erros comuns com records

- `(5).n` — acessar campo de um número: erro.
- `var p := {}; p.x` — ler campo inexistente: erro.
- `var p := {}; p.x := 5` — atribuir a campo inexistente: **não** é erro (cria o campo).
- `var x := 5; x.n := 5` — atribuir campo de um número: erro.

## 10. Erros

Quando algo dá errado, a avaliação inteira termina em **erro**. Os casos possíveis são:

- usar ou atribuir a uma variável não declarada;
- chamar um valor que não é função;
- chamar uma função com número errado de argumentos;
- usar uma função como condição de `if` ou de `while`;
- acessar campo (`e.n`) de algo que não é um record, ou ler campo inexistente;
- atribuir a campo (`e.n := v`) de algo que não é um record.

Atribuir a campo inexistente **não** é erro: o campo é criado.

## 11. Referência rápida

| Construção | Forma | Tipo |
|---|---|---|
| Declarar variável | `var x := exp;` | comando |
| Atribuir variável | `x := exp;` | comando |
| Atribuir campo | `e.n := exp;` | comando |
| Declarar função | `def f(a, b) { ... }` | comando (sem `;`) |
| Expressão por efeito | `exp;` | comando |
| Bloco | `{ comandos exp }` | expressão |
| Condicional | `if exp { ... } else { ... }` | expressão |
| Função anônima | `fn(a, b) { ... }` | expressão |
| Chamada | `f(a, b)` | expressão |
| Acesso a campo | `e.n` | expressão |
| Record literal | `{ n: exp, ... }` | expressão |
| Record vazio | `{ }` | expressão |
| Repetição | `while exp { ... }` | comando (sem `;`) |

**Palavras reservadas:** `var`, `def`, `fn`, `if`, `else`, `while`.

**Identificadores:** letras, dígitos e `_`, sem começar por dígito. `this` é um identificador comum (não é palavra reservada); a convenção de usá-lo para o record corrente é do programador.

**Observações:**

- `{}` em posição de expressão é um record vazio. `{}` em posição de comando (corpo de `while`) é um bloco de comando vazio.
- `{ x: 1 }` é um record (o `:` distingue de bloco). `{ x }` é um bloco que retorna `x`. `{ x; 1 }` é um bloco que executa `x;` e retorna `1`.