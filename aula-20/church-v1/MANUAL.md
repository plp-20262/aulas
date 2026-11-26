# `MANUAL.md` — Manual do usuário de `church` v1

Este manual complementa a especificação formal da linguagem `church`
(`README-church-v1.md`). Use-o para entender a linguagem de modo geral,
executar o interpretador, rodar a suíte de testes e programar exemplos.

---

## 1. Sobre este manual

`church` é uma **variação de `aljabr` v3**: a mesma linguagem, acrescida de
duas coisas —

- um **tipo booleano explícito** (`Bool`), com os literais `verdadeiro` e
  `falso`;
- um **sistema de tipos estático**: anotações de tipo e um **verificador**
  que rejeita certos programas **antes** de executá-los.

O nome homenageia Alonzo Church (cálculo lambda simplesmente tipado, 1940).

A semântica dinâmica (as regras de avaliação) é **idêntica** à de
`aljabr` v3. Os tipos não mudam o que um programa significa; eles apenas
decidem quais programas **podem ser executados**. Em particular, `church`
adota o **apagamento de tipos** (*type erasure*): o tipo `Bool` existe só
no verificador; na execução, `verdadeiro` vale `1` e `falso` vale `0`, e as
anotações são ignoradas.

A especificação formal completa (léxico, sintaxe, semântica dinâmica e
estática) está em `README-church-v1.md`. A linha de evolução é:

```text
aljabr v3 ──> church v1   (anotações de tipo + verificador estático)
```

O código de `church` é a **evolução direta** do interpretador de
`aljabr` v3 (o cabeçalho de `church.py` registra essa derivação). Os
arquivos são:

| Arquivo | Responsabilidade |
|---------|------------------|
| `church.py` | interpretador (`eval`) e `main` (o pipeline completo) |
| `lexer.py` | o tokenizador |
| `parser.py` | o parser (AST em listas com *tag*) |
| `tipos.py` | tokens, `Erro`, `Stream` e os **tipos** (`TNum`, `TBool`, `TFun`) |
| `verifica.py` | o **verificador** de tipos (`verifica`, novo em `church`) |

---

## 2. Como executar e testar

Todos os comandos abaixo assumem que você está no diretório deste projeto
(`aula-20/church-v1`).

### Pré-requisitos

- Python 3.10 ou mais recente;
- `pytest` instalado (caso ainda não esteja):

```bash
python3 -m pip install pytest
```

### Testar

A suíte de testes fica em `tests/`. Os arquivos herdados de `aljabr` v3
foram migrados para a sintaxe anotada de `church`, e quatro arquivos novos
cobrem as funcionalidades de `church`:

| Arquivo | O que testa |
|---------|-------------|
| `test_lexer.py`, `test_parser.py`, `test_eval.py` | literais, operadores, precedência, erros |
| `test_let_parser.py`, `test_let_eval.py` | vinculações `let..in` |
| `test_fn_lexer.py`, `test_fn_parser.py`, `test_fn_eval.py` | lambdas, aplicações, escopo léxico |
| `test_if_parser.py`, `test_if_eval.py` | `if..then..else` |
| `test_letrec_parser.py`, `test_letrec_eval.py` | `letrec` |
| `test_church_lexer.py` | **novos** tokens (`:`, `->`, `Num`, `Bool`, `verdadeiro`, `falso`) |
| `test_church_parser.py` | **novas** categorias sintáticas (`tipo`, `param`) |
| `test_verifica.py` | **o verificador** (aceitos e rejeitados) |
| `test_church_eval.py` | **apagamento** de tipos (Bool → 0/1) |

Para rodar a suíte inteira:

```bash
python3 -m pytest tests
```

Para rodar apenas um arquivo, ou um único teste:

```bash
python3 -m pytest tests/test_verifica.py
python3 -m pytest tests/test_church_parser.py -k "tipo"
```

Espera-se algo como `415 passed, 2 xfailed`. Os dois `xfail` documentam
limitações conhecidas do parser (erros de subparsers não são propagados em
`parse_exp`/`parse_termo`); herdadas de `aljabr` v3.

> **Atenção:** não rode `pytest` sem caminho a partir da raiz do
> repositório — há outro pacote `tests/` em outros diretórios e a coleta
> colidiria. Sempre especifique o caminho:
> `python3 -m pytest aula-20/church-v1/tests`.

### Executar

O interpretador é o arquivo `church.py`. Ele aceita o programa de duas
maneiras: lendo um arquivo cujo nome for passado como argumento, ou lendo
da entrada padrão (`stdin`).

A partir de um arquivo `.al`:

```bash
python3 church.py exemplos/church/dobro.al
```

```
let dobro = fn (x: Num) => x * 2 in
dobro(21)

-->  42 : Num
```

A partir da entrada padrão (digite o programa e finalize com `Ctrl-D` no
macOS/Linux, ou `Ctrl-Z Enter` no Windows):

```bash
python3 church.py
```

Ou, de forma mais prática em scripts/pipe:

```bash
echo "let x = 1 in x + 2" | python3 church.py
```

```
let x = 1 in x + 2

-->  3 : Num
```

Observe a saída: o interpretador imprime o **valor** e o **tipo** calculado
pelo verificador (`valor : tipo`). Isso importa por causa do apagamento:
`let x = 5 in x < 10` tem **tipo** `Bool` mas **valor** `1`; sem imprimir o
tipo, o `Bool` se perderia.

Cada execução processa **uma única expressão** (o arquivo ou a entrada
padrão inteira é lida como um programa). Exemplos prontos estão em
`exemplos/church/`.

---

## 3. A linguagem em um minuto

### Tipos

`church` tem três formas de tipo:

| Tipo | O que classifica | Exemplo de expressão |
|------|------------------|----------------------|
| `Num` | números | `2 + 3` |
| `Bool` | `verdadeiro`, `falso` e comparações | `1 < 2` |
| `(τ₁, …, τₙ) -> τ` | funções de `n` argumentos | `fn (x: Num) => x + 1` |

A lista de parâmetros de um tipo de função é **sempre** parentesada (mesmo
vazia ou com um parâmetro):

```text
(Num) -> Num             recebe um número e devolve um número
(Num, Num) -> Bool       recebe dois números e devolve um Bool
() -> Num                não recebe argumentos e devolve um número
((Num) -> Num, Num) -> Num   recebe uma função e um número
(Num) -> (Num) -> Num    recebe um número e devolve UMA FUNÇÃO
```

### Anotações

Em `church`, **todo parâmetro** de `fn` exige anotação de tipo
(`param ::= NOME : tipo`), e o `letrec` exige o **tipo de retorno**:

```text
let dobro = fn (x: Num) => x * 2 in dobro(21)

letrec fat = fn (n: Num) : Num =>
  if n == 0 then 1 else n * fat(n - 1)
in
fat(5)

let twice = fn (f: (Num) -> Num) => fn (x: Num) => f(f(x)) in
twice(fn (n: Num) => n + 1)(0)
```

Não há anotação em `let` (o tipo é calculado) nem em `fn` comum (o tipo do
corpo é calculado a partir dos parâmetros). Escrever `fn (x) => x`,
`fn (x: Num) : Num => x` ou `let x: Num = 1 in x` é **erro sintático**.

### Booleanos e apagamento

Os literais `verdadeiro` e `falso` são **palavras reservadas** (não podem
nomear variáveis). As comparações `==` e `<` têm tipo `Bool` e só aceitam
`Num`. `if` exige condição `Bool`.

Na execução, por apagamento, não há valores booleanos:

```text
verdadeiro   →  1
falso        →  0
1 < 2        →  1   (tipo: Bool)
```

---

## 4. O pipeline e as quatro etapas de erro

`church` percorre quatro etapas antes de produzir um resultado, e um
programa pode ser recusado em cada uma delas:

```text
código fonte
   ↓  [ lexer ]        erro LÉXICO        (ex.: 2 @ 3, fn (x: Foo) => x)
   ↓  [ parser ]       erro SINTÁTICO     (ex.: fn (x) => x, 1 < 2 < 3)
   ↓  [ verificador ]  erro de TIPO       (ex.: 2 + verdadeiro, x + 1)
   ↓  [ interpretador ] erro DINÂMICO     (ex.: 1 / 0)
resultado
```

Um programa **rejeitado pelo verificador nunca executa**. Um programa
aprovado executa exatamente como em `aljabr` v3 (as anotações são
ignoradas).

### O que o verificador promete (e o que não promete)

**Promete:** se o programa for aprovado, não ocorrerão na execução:

- variável não declarada;
- operação aritmética ou comparação com valor não numérico;
- aplicação de algo que não é função, ou com número errado de argumentos;
- `if` com condição que não é `Bool`.

**Não promete** (e por isso mesmo são aceitos):

- que o programa **termina** (`letrec f = fn (n: Num) : Num => f(n) in f(1)`
  é bem tipado);
- que **não há erro** de operação parcial (`1 / 0` é bem tipado e vale
  `erro` em execução);
- que o programa faz o que o programador **queria** (`x * 2` no lugar de
  `x + 2` também é aceito).

O verificador também é **conservador**: ele rejeita programas que
executariam sem erro. Por exemplo, `if verdadeiro then 1 else 2 +
verdadeiro` é rejeitado (os dois ramos são verificados), embora a execução
nunca chegasse ao `else`.

---

## 5. Conjunto de testes

Programas e o resultado do **verificador** (com contexto Γ = ∅):

| Programa | Resultado |
|----------|-----------|
| `42` | `Num` |
| `verdadeiro` | `Bool` |
| `2 + 3 * 4` | `Num` |
| `-(2 ** 3)` | `Num` |
| `1 < 2` | `Bool` |
| `let x = 2 + 3 in x < 10` | `Bool` |
| `let x = 1 in let x = x < 2 in x` | `Bool` |
| `let x = verdadeiro in 5` | `Num` |
| `fn (x: Num) => x + 1` | `(Num) -> Num` |
| `let dobro = fn (x: Num) => x * 2 in dobro(21)` | `Num` |
| `letrec fat = fn (n: Num) : Num => if n == 0 then 1 else n * fat(n - 1) in fat(5)` | `Num` |
| `2 + verdadeiro` | erro de tipo |
| `(1 < 2) + 1` | erro de tipo |
| `1 < verdadeiro` | erro de tipo |
| `verdadeiro == verdadeiro` | erro de tipo |
| `-verdadeiro` | erro de tipo |
| `(1 < 2) < 3` | erro de tipo |
| `x + 1` | erro de tipo (`x` não declarada) |
| `let x = verdadeiro in x * 2` | erro de tipo |
| `1 / 0` | `Num` (o verificador **não** detecta divisão por zero) |

Na **execução**, todo programa aceito executa como em `aljabr` v3, com
`verdadeiro` valendo `1` e `falso` valendo `0`.

---

## 6. Exemplos em `exemplos/church/`

O diretório `exemplos/church/` contém pequenos programas que demonstram as
novidades de `church`. A tabela abaixo resume cada um:

| Arquivo | O que demonstra | Saída esperada |
|---------|-----------------|----------------|
| `dobro.al` | anotação de parâmetro (`x: Num`) | `42 : Num` |
| `fat.al` | `letrec` com tipo de retorno (`: Num`) + `if` | `720 : Num` |
| `twice.al` | tipo de função `(Num) -> Num` | `2 : Num` |
| `compose.al` | função como argumento e como retorno | `21 : Num` |
| `currying.al` | função que devolve função (`(Num) -> (Num) -> Num`) | `5 : Num` |
| `condicional.al` | parâmetro `Bool` + `if` com condição `Bool` | `30 : Num` |
| `multiplos-params.al` | vários parâmetros anotados | `6.0 : Num` |
| `booleans.al` | `Bool` com valor `1` (apagamento) | `1 : Bool` |

Para executar: `python3 church.py exemplos/church/<arquivo>.al`.

> Os arquivos `.al` no diretório `exemplos/` (fora de `exemplos/church/`)
> são os exemplos originais de `aljabr` v3, **sem** anotações. Eles não são
> mais programas válidos de `church` e ficaram como referência histórica.

---

## 7. Diferenças da versão v3 para `church`

1. **Novo tipo `Bool`** e dois literais reservados, `verdadeiro` e `falso`.
2. **Comparações** `==` e `<` têm tipo `Bool` (em v3 devolviam `1`/`0` como
   números) e `if` passa a exigir condição `Bool`.
3. **Anotações obrigatórias** nos parâmetros (`x: Num`) e no retorno do
   `letrec` (`: Num`). Não há inferência.
4. **Tipos de função** `(τ₁, …, τₙ) -> τ`, com a lista de parâmetros sempre
   parentesada.
5. **Verificação estática** antes da execução (nova etapa no pipeline) e
   **apagamento de tipos** na execução.
6. **Operador `?` (entrada) removido** — não faz parte do léxico de `church`.
7. As palavras reservadas passam a ser nove: `let`, `in`, `fn`, `letrec`,
   `if`, `then`, `else`, `verdadeiro`, `falso` (`Num` e `Bool` são
   categorias léxicas próprias, não palavras reservadas).

A semântica dinâmica não mudou: `church` executa o programa de `aljabr` v3
que resulta de apagar as anotações e trocar `verdadeiro` por `1` e `falso`
por `0`.
