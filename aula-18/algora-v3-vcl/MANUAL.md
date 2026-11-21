# Manual de Algora (v3) (vCl)

**Algora** é uma pequena linguagem que mistura três ideias:

- do lado funcional (herdado de Aljabr): funções são valores, podem ser anônimas e capturam o ambiente onde foram criadas (*closures*);
- do lado imperativo (inspirado em Algol): variáveis mutáveis, atribuição com `:=` e programas escritos como sequência de comandos;
- do lado dos dados (a partir da v3): **registros** mutáveis, como os objetos literais de JavaScript: `{ x: 1, y: 2 }`. Combinados com closures e mutação, eles bastam para escrever programas **orientados a objetos**, sem nenhuma construção nova.

Há ainda um toque de Rust: **tudo que termina com uma expressão devolve o valor dela**. Não existe `return`.

Este manual mostra como usar a linguagem. Para as regras formais (gramática e semântica operacional), consulte o `README.md`.

## 1. Primeiro programa

Um programa é uma lista de comandos terminados em `;`, seguida de **uma
expressão final** (sem `;`). O valor dessa expressão é o resultado do programa.

```
var x := 10;
var y := 20;
x + y
```

Resultado: `30`.

> Todo programa precisa ter a expressão final. Um programa que termina em `;` é um erro de sintaxe.

Algora não tem comentários.


## 2. Valores e operadores

Os valores são **números**, **funções** e **registros**. Os literais numéricos são inteiros (`0`, `42`), mas o tipo numérico é o dos reais, então `/` pode produzir resultados fracionários.

| Operador | Significado | Observação |
|---|---|---|
| `e.f`, `f(x)` | acesso a campo, chamada | associam à esquerda e se combinam: `f(1).g(2)` |
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
- Os operadores aritméticos e de comparação só se aplicam a **números**. Aplicá-los a um registro (inclusive `==`) é erro.

**Verdadeiro e falso** são números: `0` é falso e qualquer outro número é verdadeiro. Por isso `if` aceita qualquer número como condição, e usar uma função ou um registro como condição é um erro.


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

Os dois usos de `:=` parecem iguais, mas fazem coisas diferentes: `var x := e` cria uma variável (escondendo qualquer `x` anterior), enquanto `x := e` altera a que já existe. Há ainda um terceiro uso, a partir da v3: `e.campo := exp` altera (ou cria) um campo de um registro (veja a seção "Registros").


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

- Laços são feitos com `while` (veja a seção "Laços com `while`").
- Funções são valores comuns: podem ser passadas como argumento, devolvidas e guardadas em variáveis (e, a partir da v3, em campos de registros).
- Chamadas encadeiam: `f(1)(2)` chama `f(1)` e aplica o resultado a `2`.
- Os argumentos são avaliados da esquerda para a direita e passados **por valor**. Os parâmetros são variáveis locais, então atribuir a um parâmetro não afeta o chamador.
- Chamar algo que não é função, ou passar o número errado de argumentos, é erro.

```
def duas_vezes(f, x) { f(f(x)) }
duas_vezes(fn(n) { n * 2 }, 5)
```

Resultado: `20`.

> Para recursão, use `def`. Com `var f := fn(n) { ... f(n - 1) ... }`, o nome `f` ainda não existe quando a função é criada, então a chamada recursiva falha.


## Laços com `while`

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
- A condição é numérica, como em `if`. Usar uma função ou um registro como condição de `while` é erro.


## Registros

Um **registro** agrupa valores sob nomes, chamados **campos**. Escreve-se `{ nome: exp, ... }` e lê-se um campo com `.`:

```
var p := { x: 3, y: 4 };
p.x * p.x + p.y * p.y
```

Resultado: `25`.

Regras do literal:

- Os campos são separados por vírgula, sem vírgula depois do último. Os nomes de um mesmo registro devem ser **distintos** (repetir um nome é erro de sintaxe) e não podem ser palavras reservadas.
- `{}` é o registro vazio.
- O valor de um campo pode ser qualquer valor: número, função ou outro registro. As expressões dos campos são avaliadas da esquerda para a direita.
- Os nomes de campo **não são variáveis**: vivem num espaço próprio. Em `var x := 5; { x: x + 1 }.x`, o `x` antes dos dois-pontos é o nome do campo e o `x` depois é a variável. O resultado é `6`.
- Acessos e chamadas encadeiam: `a.b.c`, `f(1).x`, `o.metodo(2)`.

```
var seg := { a: { x: 0, y: 0 }, b: { x: 3, y: 4 } };
seg.b.x
```

Resultado: `3`.

### Alterando campos

`e.campo := exp;` é um **comando** (termina em `;`, como qualquer atribuição) que altera o campo de um registro:

```
var p := { x: 3, y: 4 };
p.x := p.x + 10;
p.x
```

Resultado: `13`.

Há uma diferença em relação às variáveis: atribuir a um campo que **ainda não existe** não é erro, e o campo passa a existir. Campos não são declarados, e é assim que se constrói um registro aos poucos:

```
var r := {};
r.a := 1;
r.b := r.a + 1;
r.a + r.b
```

Resultado: `3`.

Já **ler** um campo que não existe é erro.

### Registros são referências

Números são copiados ao serem atribuídos. Registros, não: uma variável guarda uma **referência** ao registro. Atribuir a outra variável, guardar em outro registro ou passar para uma função copia a referência, e todos passam a enxergar o mesmo registro:

```
var a := { n: 1 };
var b := a;
b.n := 5;
a.n
```

Resultado: `5`. Compare com números: depois de `var a := 1; var b := a; b := 2;`, o valor de `a` continua `1`.

O mesmo vale para argumentos. Uma função pode alterar os campos de um registro recebido:

```
var c := { n: 7 };
def zera(r) { r.n := 0; 0 }
zera(c);
c.n
```

Resultado: `0`. Já atribuir ao próprio parâmetro (que é uma variável local) não afeta o chamador:

```
var c := { n: 7 };
def troca(r) { r := { n: 99 }; r.n := r.n + 1; 0 }
troca(c);
c.n
```

Resultado: `7`. Dentro de `troca`, `r` passou a apontar para um registro novo, e `c` continua apontando para o antigo.

Por fim, `==` e `<` só comparam números: comparar dois registros é erro.

### `{` abre um bloco ou um registro?

Os dois usam chaves. O `{` abre um **registro** quando vem seguido de `}` ou de `nome:`; caso contrário abre um **bloco**. Como todo bloco precisa de uma expressão final, `{}` nunca é um bloco.

Nos lugares em que a linguagem exige um bloco (os dois ramos do `if` e o corpo de `def`, `fn` e `while`), o `{` abre sempre um bloco. Para devolver um registro de lá, escreva o registro como expressão final do bloco, entre chaves extras:

```
var f := fn(a) { { x: a, y: a + 1 } };
f(1).y
```

Resultado: `2`. As chaves de fora são o corpo de `fn`; as de dentro são o registro.

```
var n := 3;
var r := if n < 10 { { ok: 1 } } else { {} };
r.ok
```

Resultado: `1`.


## 7. Closures e estado

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


## Objetos

Algora **não tem classes**, nem `this`, nem uma construção especial para "método". E não precisa: a linguagem já tem tudo de que um objeto básico precisa.

| O que um objeto precisa | O que Algora já tinha |
|---|---|
| estado que muda com o tempo | variáveis mutáveis (`var`, `:=`) |
| comportamento que lembra o estado | closures (seção 7) |
| agrupar o comportamento (e o estado) sob nomes | registros (seção "Registros") |

Um **objeto** é, portanto, um registro cujos campos são funções (os "métodos"). E **chamar um método** não tem nada de novo: `o.m(x)` lê o campo `m` do registro `o` e aplica a função que está lá, exatamente como `f(x)` aplicaria uma função guardada numa variável.

### Estado privado

Basta uma função que cria as variáveis de estado e devolve um registro de closures sobre elas:

```
def Conta(saldo_inicial) {
  var saldo := saldo_inicial;
  {
    depositar: fn(v) { saldo := saldo + v; saldo },
    sacar: fn(v) { saldo := saldo - v; saldo },
    consultar: fn() { saldo }
  }
}
var c := Conta(100);
c.depositar(50);
c.sacar(30);
c.consultar()
```

Resultado: `120`. O estado (`saldo`) é **privado**: ele não é um campo do registro, e só as closures conseguem enxergá-lo. Fora da função `Conta`, não há como ler ou alterar `saldo` a não ser pelos "métodos". (O registro devolvido é a expressão final do corpo de `Conta`, por isso pode vir logo depois do `var`.)

### Objeto que se referencia: o padrão `este`

Se o estado deve ser um campo (visível de fora) ou se um método precisa do próprio objeto, a convenção é criar primeiro o registro vazio, guardá-lo numa variável (aqui chamada `este`) e depois preencher os campos:

```
def Contador() {
  var este := {};
  este.n := 0;
  este.inc := fn() { este.n := este.n + 1; este.n };
  este.dec := fn() { este.n := este.n - 1; este.n };
  este.get := fn() { este.n };
  este
}
var c1 := Contador();
var c2 := Contador();
c1.inc();
c1.inc();
c1.inc();
c1.dec();
c2.inc();
c1.get() + 1000 * c2.get()
```

Resultado: `1002` (`c1` termina com `2`, `c2` com `1`).

O que acontece aqui:

- Cada chamada a `Contador()` cria um registro novo e uma variável `este` nova que aponta para ele. Por isso `c1` e `c2` são independentes.
- As closures `inc`, `dec` e `get` capturam a variável `este` do lugar onde foram criadas. Elas enxergam o registro de **seu** objeto, e `este.n := ...` altera esse registro.
- Como registros são referências, o registro que `Contador()` devolve (`c1`) é o mesmo que `este` enxerga. Por isso `c1.get()` vê o que `c1.inc()` fez, e `c1.n` também funcionaria: o estado aqui é público.
- Por que não escrever `var este := { get: fn() { este.n } }`? Pelo mesmo motivo da nota sobre recursão na seção 6: enquanto o literal é avaliado, o nome `este` ainda não existe. Daí o registro vazio primeiro, e os campos depois.

Informalmente, diz-se que `c1.inc()` "envia a mensagem `inc` ao objeto `c1`". Para a linguagem, é só ler um campo e chamar a função encontrada.


## 8. Erros

Quando algo dá errado, a avaliação inteira termina em **erro**. Os casos possíveis são:

- usar ou atribuir a uma variável não declarada;
- chamar um valor que não é função (inclusive um registro);
- chamar uma função com número errado de argumentos;
- usar uma função ou um registro como condição de `if` ou de `while`;
- aplicar um operador aritmético ou de comparação a algo que não é número (por exemplo, `==` entre dois registros);
- ler ou atribuir um campo (`e.f`, `e.f := ...`) de algo que não é registro;
- ler um campo que o registro não tem.

Há também erros de sintaxe específicos de registros: repetir o nome de um campo no mesmo literal (`{ a: 1, a: 2 }`) e atribuir a algo que não é variável nem campo (`f() := 1`).


## 9. Referência rápida

| Construção | Forma | Tipo |
|---|---|---|
| Declarar variável | `var x := exp;` | comando |
| Atribuir | `x := exp;` | comando |
| Atribuir a campo | `e.f := exp;` | comando |
| Declarar função | `def f(a, b) { ... }` | comando (sem `;`) |
| Expressão por efeito | `exp;` | comando |
| Bloco | `{ comandos exp }` | expressão |
| Condicional | `if exp { ... } else { ... }` | expressão |
| Função anônima | `fn(a, b) { ... }` | expressão |
| Chamada | `f(a, b)` | expressão |
| Registro | `{ a: exp, b: exp }`, `{}` | expressão |
| Acesso a campo | `e.f` | expressão |
| Repetição | `while exp { ... }` | comando (sem `;`) |

**Palavras reservadas:** `var`, `def`, `fn`, `if`, `else`, `while`.

**Identificadores:** letras, dígitos e `_`, sem começar por dígito. Os nomes de campo seguem a mesma regra (e também não podem ser palavras reservadas).
