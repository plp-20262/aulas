# `MANUAL.md` — Manual do usuário de `aljabr` v3

Este manual é o complemento da especificação formal (`README.md`). Use-o para
entender de modo geral a linguagem, executar o interpretador, rodar a suíte de
testes e programar exemplos. O essencial da especificação formal (léxico,
sintaxe e semântica) está em `README.md`.

---

## 1. Sobre este manual

`aljabr` é uma mini-linguagem funcional projetada para um curso de Linguagens
de Programação. Na versão `v3` ela inclui:

- vinculações locais (`let .. in`) e vinculações recursivas (`letrec`);
- funções anônimas (`fn`) e aplicações (`f(args)`);
- condicional especial (`if .. then .. else`), preguiçoso nos ramos;
- operadores aritméticos (`+ - * / **`), unários (`+ -`) e de comparação
  (`== <`);
- operador de entrada (`?`, lê um inteiro da entrada padrão);
- valores: números (inteiros e floats), closures e o valor especial `erro`.

A especificação formal completa está em `README.md`. Este manual foca em como
**executar**, **testar** e **usar** a linguagem.

---

## 2. Como executar e testar

Todos os comandos abaixo assumem que você está no diretório deste projeto
(`aula-17/aljabr-v3`).

### Pré-requisitos

- Python 3.10 ou mais recente;
- `pytest` instalado (caso ainda não esteja):

```bash
python3 -m pip install pytest
```

### Testar

A suíte de testes fica no diretório `tests/` e é dividida nos seguintes
arquivos:

| Arquivo                    | O que testa                                                                        |
|----------------------------|------------------------------------------------------------------------------------|
| `tests/test_lexer.py`      | o tokenizador (literais, operadores, `NOME`, palavras reservadas, erros léxicos)   |
| `tests/test_parser.py`     | o parser de expressões aritméticas (bem formadas e erros)                          |
| `tests/test_eval.py`       | o avaliador `eval` (operadores, precedência, propagação de erros)                  |
| `tests/test_let_parser.py` | o parser das vinculações `let..in`                                                 |
| `tests/test_let_eval.py`   | o avaliador `eval` para variáveis e `let..in`                                      |
| `tests/test_fn_parser.py`  | o parser de lambdas e aplicações                                                   |
| `tests/test_fn_eval.py`    | o avaliador `eval` para lambdas, aplicações e escopo léxico                        |
| `tests/test_if_parser.py`  | o parser de `if..then..else`                                                       |
| `tests/test_if_eval.py`    | o avaliador `eval` para `if`                                                       |
| `tests/test_letrec_parser.py` | o parser de `letrec`                                                              |
| `tests/test_letrec_eval.py` | o avaliador `eval` para `letrec`                                                   |

Para rodar a suíte inteira:

```bash
python3 -m pytest tests
```

Para rodar apenas um arquivo, ou um único teste:

```bash
python3 -m pytest tests/test_lexer.py
python3 -m pytest tests/test_parser.py -k "unclosed_paren"
```

Espera-se algo como `331 passed, 2 xfailed`. Os dois `xfail` são testes que
documentam **limitações conhecidas** do parser atual (erros de subparsers não
são propagados em `parse_exp`/`parse_termo`); eles falham de propósito e
devem começar a passar quando o parser for corrigido.

Observações:

- não há `pyproject.toml` nem `setup.py` neste diretório, de propósito: os
  testes rodam direto da fonte. Por isso use sempre `python3 -m pytest`
  (e não apenas `pytest`) e passe o diretório dos testes explicitamente;
- **não rode `pytest` sem caminho a partir da raiz do repositório**: há
  outro pacote chamado `tests/` em `aula-11/aljabr-v1` e a coleta
  colidiria. Sempre especifique o caminho, por exemplo:
  `python3 -m pytest aula-17/aljabr-v3/tests`.

### Executar

O interpretador é o arquivo `aljabr.py`. Ele aceita o programa de duas
maneiras: lendo um arquivo cujo nome for passado como argumento, ou lendo
da entrada padrão (`stdin`).

A partir de um arquivo `.al`:

```bash
python3 aljabr.py prog1.al
```

```
let x = 2 in
let y = x ** 2 in
let z = y + 1 in
x + y + z

-->  11
```

A partir da entrada padrão (digite o programa e finalize com `Ctrl-D` no
macOS/Linux, ou `Ctrl-Z Enter` no Windows):

```bash
python3 aljabr.py
```

Ou, de forma mais prática em scripts/pipe:

```bash
echo "let x = 1 in x + 2" | python3 aljabr.py
```

```
let x = 1 in x + 2

-->  3
```

Cada execução do interpretador processa **uma única expressão** (o arquivo
ou a entrada padrão inteira é lida como um programa). Exemplos de programas
prontos estão no diretório `exemplos/`.

---

## 3. Conjunto de testes

Use os programas abaixo para testar sua implementação. Cada programa passa
por lexer, parser e `eval` (helper `run` de `tests/conftest.py`).

| Programa                                                           | Resultado |
|--------------------------------------------------------------------|-----------|
| `let quad = fn (x) => x * x in quad(3) + quad(5)`                  | `34`      |
| `(fn (x, y) => x + y)(2, 3)`                                       | `5`       |
| `(fn () => 42)()`                                                  | `42`      |
| `(fn (x) => fn (y) => x + y)(2)(3)`                                | `5`       |
| `let n = 7 in let soma_n = fn (x) => x + n in let n = 100 in soma_n(3)` | `10` |
| `let f = fn (x) => x in -f(2)`                                     | `-2`      |
| `let f = fn (x) => x in f(2) ** 2`                                 | `4`       |
| `let f = fn (x) => x + y in 10`                                    | `10`      |
| `let a = 10 in let f = fn (x) => x + a in let a = 20 in f(5)`      | `15`      |
| `let x = 1 in (fn (x) => x)(9)`                                    | `9`       |
| `let g = fn (x) => fn (y) => x + y in g(10)(5)`                    | `15`      |
| `let inc = fn (x) => x + 1 in (fn (f, x) => f(f(x)))(inc, 1)`      | `3`       |
| `let dobra = fn (x) => fn (y) => x * y in let d5 = dobra(5) in d5(2) + d5(3)` | `25` |
| `letrec fat = fn (n) => if n == 0 then 1 else n * fat(n - 1) in fat(3)` | `6` |
| `let f = fn (x, y) => x + y in f(1)`                               | `erro`    |
| `5(3)`                                                             | `erro`    |
| `let q = fn (x) => x in q + 1`                                     | `erro`    |
| `let f = fn (x) => x + y in f(1)`                                  | `erro`    |
| `let x = 1/0 in 5`                                                 | `erro`    |
| `(fn (x) => 5)(1/0)`                                               | `erro`    |
| `if (fn (x) => x) then 2 else 3`                                   | `erro`    |
| `letrec f = fn (x, y) => x in f(1)`                                | `erro`    |

E os programas abaixo devem ser **rejeitados pelo parser**:
`fn x => x`, `fn (x,) => x`, `f(1,)`, `fn (x) x`, `1 + fn (x) => x`,
`let fn = 1 in fn`, `if x then 1`, `letrec x = 5 in x`,
`1 + if 1 then 2 else 3`, `let if = 1 in if`.

---

## 4. Exemplos em `exemplos/`

O diretório `exemplos/` contém programas prontos em `aljabr` v3. A tabela
abaixo resume cada um, o que demonstra e a saída esperada ao executar
`python3 aljabr.py exemplos/<arquivo>.al`.

| Arquivo | O que demonstra | Saída esperada |
|---------|-----------------|----------------|
| `prog1.al` | `let` aninhado e exponenciação | `11` |
| `prog2.al` | funções com múltiplos parâmetros | `12` |
| `raiz-de-2-babilonios.al` | altas ordens, `twice`, ponto fixo aproximado | `1.414213562373095` |
| `twice.al` | aplicação de funções como argumentos | `16` |
| `dobro-e-triplo.al` | composição simples de funções | `6` |
| `funcao-simples.al` | função com vários parâmetros | `50` |
| `closures-simples.al` | closures e funções de primeira classe | `32` |
| `compose.al` | composição de funções | `23` |
| `fatorial2.al` | `letrec` + `if` + comparação (fatorial recursivo) | `720` |
| `contador.al` | `letrec` + `if` + recursão | `0` |
| `if4.al` | `if` nativo (preguiçoso nos ramos) | `1` |
| `if.al` | `if` codificado em Church (estrito: avalia ambos ramos) | `1` |
| `if2.al` | `if` em Church: ramo não escolhido com divisão por zero → `erro` | `erro: divisão por zero` |
| `if3.al` | `if` em Church com thunks (adiação de avaliação) | `1` |
| `booleans.al` | booleans em Church (várias expressões no arquivo) | *erro de sintaxe* (uma expressão por execução) |
| `fatorial.al` | `let if = ...` — `if` é palavra reservada em v3 | *erro de sintaxe* |
| `omega.al` | não-terminação: `(fn (x) => x(x))(fn (x) => x(x))` | não termina (`RecursionError`) |
| `omega2.al` | não-terminação: `let m = fn (x) => x(x) in m(m)` | não termina (`RecursionError`) |
| `omega3.al` | não-terminação com `letrec` implícito | não termina (`RecursionError`) |

Notas:

- `booleans.al` contém várias expressões de nível superior no mesmo arquivo.
  O interpretador aceita **uma única expressão** por execução, então esse
  arquivo gera um erro de sintaxe ("tokens depois da expressão").
- `fatorial.al` vincula o nome `if` em um `let`. Em `aljabr` v3, `if` é uma
  palavra reservada, portanto não pode ser usado como nome de variável; o
  parser rejeita o programa.
- Os programas `omega*`, `omega2.al` e `omega3.al` expressam não-terminação
  (ponto fixo de Curry). O interpretador esgota a pilha de recursão do Python
  (`RecursionError`) em vez de rodar para sempre.

---

## 5. Diferenças da versão v2 para a v3

1. Novas palavras reservadas: `letrec`, `if`, `then`, `else`.
2. Novos operadores: `==` (igualdade) e `<` (menor que), no novo nível
   `comp`, não-associativo.
3. `if c then e1 else e2`: condicional especial, preguiçoso nos ramos
   (apenas o ramo escolhido é avaliado).
4. `letrec f = fn (...) => e in e2`: definição recursiva com vínculo
   genuíno (o nome `f` está visível no próprio corpo de `f`).
5. `atomo` aceita `let NOME = exp in exp`.
6. O corpo aditivo da v2 (`termo { (+|-) termo }`) foi renomeado para `soma`.

O poder computacional da v2 já era Turing equivalente; a v3 adiciona
conveniência para expressar seleção de caminhos e recursão de forma direta.
