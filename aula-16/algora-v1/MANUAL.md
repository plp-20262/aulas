# Manual de Algora

**Algora** é uma pequena linguagem que mistura duas ideias:

- do lado funcional (herdado de Aljabr): funções são valores, podem ser anônimas e capturam o ambiente onde foram criadas (*closures*);
- do lado imperativo (inspirado em Algol): variáveis mutáveis, atribuição com `:=` e programas escritos como sequência de comandos.

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

Os valores são **números** e **funções**. Os literais são inteiros (`0`, `42`), mas o tipo numérico é o dos reais, então `/` pode produzir resultados fracionários.

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

- Não existem laços (`while`, `for`). A repetição é feita com recursão.
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


## 8. Erros

Quando algo dá errado, a avaliação inteira termina em **erro**. Os casos possíveis são:

- usar ou atribuir a uma variável não declarada;
- chamar um valor que não é função;
- chamar uma função com número errado de argumentos;
- usar uma função como condição de `if`.


## 9. Referência rápida

| Construção | Forma | Tipo |
|---|---|---|
| Declarar variável | `var x := exp;` | comando |
| Atribuir | `x := exp;` | comando |
| Declarar função | `def f(a, b) { ... }` | comando (sem `;`) |
| Expressão por efeito | `exp;` | comando |
| Bloco | `{ comandos exp }` | expressão |
| Condicional | `if exp { ... } else { ... }` | expressão |
| Função anônima | `fn(a, b) { ... }` | expressão |
| Chamada | `f(a, b)` | expressão |

**Palavras reservadas:** `var`, `def`, `fn`, `if`, `else`.

**Identificadores:** letras, dígitos e `_`, sem começar por dígito.
