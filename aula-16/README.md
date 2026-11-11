# Aula 16 — Unidade 5 (2/3)

> Tema da aula: repetição com estado. Adicionamos o comando `while` a `algora`.
>
> Observação: como `if` já existe em Algora (expressão, `else` obrigatório), o
> foco desta aula passa a ser **repetição de comandos que alteram o store**.
> Os resultados dos exemplos abaixo vêm da especificação; vale rodá-los na
> implementação antes da aula.


## Roteiro (≈ 2h, ajuste os tempos)

| # | Bloco                                                        | Min |
|---|--------------------------------------------------------------|-----|
| 1 | Retomada: ambiente × store; rodar o contador na implementação | 10 |
| 2 | Demo de Algora atual (exemplos abaixo)                       | 15  |
| 3 | Motivação: repetir **comandos** que mudam estado             | 10  |
| 4 | Decisões de design do `while`                                | 10  |
| 5 | Especificação: léxico, EBNF, semântica                       | 25  |
| 6 | Rastreamento (tabela de `i` e `soma`) e derivação curta      | 10  |
| 7 | Implementação ao vivo: lexer, parser, `eval`                 | 30  |
| 8 | Fechamento, tarefa, linha de Algora na tabela de síntese     | 5   |

**Se o tempo apertar:** corte o bloco 2 pela metade e a derivação do bloco 6.
Mantenha as decisões de design, as três regras e a implementação.


## Exemplos da versão atual de Algora

```text
// 1. contador (closure sobre localização mutável): resultado 3
def criaContador() {
    var n := 0;
    fn () { n := n + 1; n }
}
var c := criaContador();
c();
c();
c()
```

```text
// 2. dois contadores independentes (cada chamada aloca um novo n)
var a := criaContador();
var b := criaContador();
a();
a();
b()                      // 1
```

```text
// 3. a closure captura a localização, não o valor (em aljabr seria 10)
var x := 10;
def f() { x }
x := 20;
f()                      // 20
```

```text
// 4. bloco com subescopo: o var interno cria outra localização
var x := 1;
var y := { var x := 10; x + 1 };
x + y                    // 12
```

```text
// 5. recursão com def + if
def fat(n) { if n == 0 { 1 } else { n * fat(n - 1) } }
fat(5)                   // 120
```

```text
// 6. if com efeito colateral: note o ";" e o 0 final dos blocos
var x := 0;
if 1 { x := 5; 0 } else { 0 };
x                        // 5
```

```text
// 7. erros
y := 1; 0                // erro (AssignNaoDeclarada)
(fn (a) { a })(1, 2)     // erro (AppAridade)
```

> O exemplo 6 é um bom gancho: o corpo de um bloco **exige uma expressão
> final**, o que fica estranho num laço.


## Decisões de design (bloco 4)

1. **Comando, não expressão.** Como `def`, `while` não produz valor, o que evita
   decidir "quanto vale um laço". Consequência: não precisa de `;` depois do
   bloco e não pode ser a última coisa de um bloco.
2. **Corpo como `bloco_cmd`**: uma sequência de comandos **sem** expressão
   final, `{ comando* }`. A alternativa, reusar `bloco`, forçaria um `0`
   descartável no fim de todo laço. Recomendação: `bloco_cmd` (custa só uma
   função nova no parser).
3. **Palavra reservada `while`**, por coerência com `var`, `def`, `if` e
   `else` (a lista passa a ter 6). Se preferir `enquanto`, troque só o lexema.
4. **Condição numérica**, igual ao `if`: `0` é falso. Closure na condição dá
   `erro`.


## Especificação

### Léxico

```text
WHILE ::= while        ← NOVO (palavra reservada)
```

Nenhuma outra mudança.

### Sintaxe (EBNF)

```text
comando    ::= func_decl
             | var_decl ;
             | atribuicao ;
             | while_cmd                      ← NOVO (sem ";")
             | exp ;

while_cmd  ::= while exp bloco_cmd            ← NOVO
bloco_cmd  ::= LBRACE { comando } RBRACE      ← NOVO
```

Continua LL(1): `WHILE` decide a alternativa em `comando`. Não há conflito
entre a condição e o `{`, porque `{` só inicia `bloco` quando aparece no começo
de um `atomo`; em `i < 3 {` a condição já está completa.

Sintaxe abstrata: `While(cond, corpo)`.

### Semântica

A relação de comandos continua $\langle c,\rho,\sigma\rangle \rightarrow
\langle\rho',\sigma'\rangle$.

Primeiro, o bloco de comandos, que executa em sequência e **descarta o
ambiente final** (o escopo do corpo morre, mas o store persiste):

$$
\frac{
  \langle c_1,\rho,\sigma_0\rangle \rightarrow \langle\rho_1,\sigma_1\rangle \quad\cdots\quad
  \langle c_n,\rho_{n-1},\sigma_{n-1}\rangle \rightarrow \langle\rho_n,\sigma_n\rangle
}{
  \langle \{c_1 \dots c_n\},\rho,\sigma_0\rangle \Downarrow_{s} \sigma_n
} \quad \text{(BlocoCmd)}
$$

Depois, o laço:

$$
\frac{
  \langle c,\rho,\sigma\rangle \Downarrow \langle 0,\sigma_1\rangle
}{
  \langle \mathtt{while}\ c\ b,\rho,\sigma\rangle \rightarrow \langle\rho,\sigma_1\rangle
} \quad \text{(WhileFalso)}
$$

$$
\frac{
  \langle c,\rho,\sigma\rangle \Downarrow \langle n,\sigma_1\rangle \ (n\in ℝ,\ n\neq 0) \qquad
  \langle b,\rho,\sigma_1\rangle \Downarrow_{s} \sigma_2 \qquad
  \langle \mathtt{while}\ c\ b,\rho,\sigma_2\rangle \rightarrow \langle\rho,\sigma_3\rangle
}{
  \langle \mathtt{while}\ c\ b,\rho,\sigma\rangle \rightarrow \langle\rho,\sigma_3\rangle
} \quad \text{(WhileVerd)}
$$

$$
\frac{
  \langle c,\rho,\sigma\rangle \Downarrow \langle v_c,\sigma_1\rangle \qquad v_c\in\mathrm{Clo}
}{
  \langle \mathtt{while}\ c\ b,\rho,\sigma\rangle \rightarrow \mathbf{erro}
} \quad \text{(WhileCondFuncao)}
$$

Pontos para comentar:

- **A 3ª premissa de (WhileVerd) contém o próprio `while`**: a regra é
  recursiva, e é essa recursão que faz o laço repetir.
- **A semântica passa a ser parcial.** Em `while 1 { }` não existe derivação
  alguma. É a primeira vez no curso que a não-terminação aparece de forma
  explícita nas regras. Determinismo continua valendo; totalidade, não.
- O ambiente **não** muda: um `var` dentro do corpo não é visível depois do
  laço.
- **Conexão com a Aula 15 (açúcar sintático):** `while c b` equivale a uma
  função recursiva, mas o `while` é mais direto e não consome a pilha de
  Python:

```text
{ def loop() { if c { b; loop() } else { 0 } }  loop() }
```


## Exemplos com `while`

```text
var i := 0;
var soma := 0;
while i < 5 {
    soma := soma + i;
    i := i + 1;
}
soma                     // 10
```

Tabela de rastreamento para esse programa (callback à Aula 01):

| iteração | `i` antes | `i < 5` | `soma` depois |
|----------|-----------|---------|---------------|
| 1        | 0         | 1       | 0             |
| 2        | 1         | 1       | 1             |
| 3        | 2         | 1       | 3             |
| 4        | 3         | 1       | 6             |
| 5        | 4         | 1       | 10            |
| fim      | 5         | 0       | 10            |

```text
def fatIter(n) {
    var r := 1;
    var i := 1;
    while i < n + 1 { r := r * i; i := i + 1; }
    r
}
fatIter(5)               // 120
```


## Implementação ao vivo (bloco 7)

- **Lexer:** `while` no mapa de reservadas.
- **Parser:** em `parse_comando`, `if peek(WHILE)` chama `parse_while`, que faz
  `expect(WHILE)`, `cond = parse_exp`, `corpo = parse_bloco_cmd` e devolve
  `While(cond, corpo)`. `parse_bloco_cmd` é um `while not peek(RBRACE)` que
  chama `parse_comando`.
- **Eval:** use um **laço Python**, não recursão. Avalie a condição e, se for
  `Erro`, propague. Se for closure, devolva `Erro`. Se for `0`, pare. Caso
  contrário, execute o corpo em uma cópia do ambiente (o store é compartilhado)
  e repita.
- **Testes:** os dois exemplos acima; `while 0 { }` (não executa); condição com
  closure (`erro`); `var` interno invisível depois do laço.


## Tarefa e fechamento

1. Derivar a execução de `var i := 0; while i < 2 { i := i + 1; } i` com as
   regras.
2. Um `var` dentro do corpo, com closure criada em cada iteração: as closures
   compartilham a localização ou cada uma tem a sua?
3. **(Desafio)** Propor `break` e dizer o que muda nas regras (dica: o
   resultado do comando precisa sinalizar a saída).
4. Preencher a linha de Algora na tabela de síntese: estado **sim**, controle
   `if` (expressão) e `while` (comando).
