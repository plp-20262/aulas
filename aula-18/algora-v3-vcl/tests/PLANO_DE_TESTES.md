# Testes adicionais para o interpretador de Algora (black box)

Derivados **apenas** da especificação (README.md) e da API observada nos testes
existentes (`tokenizador`, `parser`, `executar_programa(prog, {}, {})`, `Erro.msg`,
`TokenType`, nós `Block/VarDecl/Assign/FunDecl/ExprStmt/Num/Var/BinaryOp/Call/IfExpr/AnonFun`).
Os arquivos novos **não substituem** nenhum arquivo existente: basta copiá-los para o
diretório `tests/` e rodar `pytest`.

## Mapa dos módulos

| Arquivo | Foco |
|---|---|
| `test_lexer_nomes.py` | NOME, reservadas (case-sensitive, prefixos), INTEIRO (zeros à esquerda, `1x`) |
| `test_lexer_simbolos.py` | maximal munch (`**`/`*`, `==`/`=`, `:=`/`=`), sem literal negativo, espaços |
| `test_lexer_erros.py` | caracteres fora da linguagem, decimais, ASCII-only, `token desconhecido` |
| `test_parser_programa.py` | forma do programa, `;`, `def` sem `;`, falta de expressão final |
| `test_parser_blocos.py` | bloco como átomo/comando, bloco vazio, sem expressão final |
| `test_parser_expressoes.py` | tabela de expressões válidas; comparação não-associativa; um único sinal; `if`/`fn` não são operandos |
| `test_if_parser_extra.py` | formas do `if`, inexistência de `else if`, ramos obrigatoriamente blocos |
| `test_fn_parser_extra.py` | `fn`, chamadas encadeadas, vírgulas finais, `fn(...){}(x)` inválido |
| `test_let_parser_extra.py` | `var`/`:=`: atribuição não é expressão, alvo deve ser NOME, `=` inválido |
| `test_letrec_parser_extra.py` | `def`: parâmetros, aninhamento, `def` não é expressão |
| `test_eval_aritmetica.py` | precedência, associatividade, `**` à direita, `-2 ** 2 == 4`, divisão real |
| `test_eval_comparacao.py` | resultado 1/0, precedência, `<`/`==` sobre funções = erro |
| `test_eval_erros.py` | todas as regras de erro, propagação, avaliação ansiosa, erros léxicos/sintáticos via `executar_programa` |
| `test_eval_ordem.py` | ordem esquerda→direita, estado enfiado entre operandos, RHS antes de gravar |
| `test_eval_programa.py` | independência entre execuções, espaçamento, programas longos/aninhados |
| `test_let_eval_extra.py` | `var` redeclarado × `:=`, sem aliasing, parâmetros por valor, locais frescos por chamada |
| `test_letrec_eval_extra.py` | `def`: sem hoisting, recursão mútua por atribuição, redefinição, clássicos (fat, fib, gcd, Ackermann) |
| `test_fn_eval_extra.py` | closures (captura por referência, estado privado), escopo léxico, ordem superior, currying |
| `test_if_eval_extra.py` | verdade = qualquer real ≠ 0 (inclui 1/2), ramos preguiçosos, escopo dos ramos |
| `test_block_eval.py` | sub-escopo, sombreamento, vazamento, atribuição a variável externa |
| `test_programas_eval.py` | integração: numerais de Church, combinador Z, primos, Collatz, conta bancária, Newton |

## Decisões de interpretação da especificação (se um teste falhar, confira aqui)

Estes testes seguem a gramática/semântica *ao pé da letra*; alguns podem divergir de
uma decisão de projeto sua. Cada um está num teste de nome autoexplicativo:

1. `-2 ** 2 == 4` (`fator ::= unario [** fator]`: o sinal prende mais forte que `**`).
2. Um único sinal unário: `--1` é erro de sintaxe; já `1 - -1` e `1--2` são válidos.
3. `/` é divisão **real** (domínio ℝ): `7 / 2 == 3.5`; `if 1/2` é verdadeiro.
4. `if`/`fn` não são operandos sem parênteses (`1 + if ...`, `fn(x){x}(1)` são erro); não existe `else if`.
5. Não existe comando vazio: `def f() {1}; f()` e `;;` são erro. `{ 1 } 2` também (falta `;`).
6. Sem *hoisting*: `def f() { g() } def g() {1} f()` é erro; `var f := fn..{f(..)}` não recursa.
7. `var x` repetido aloca **novo** endereço (closures antigas continuam vendo o antigo); `:=` escreve no mesmo.
8. Nomes de `def` são atribuíveis (`f := 5`), e a recursão passa pelo endereço de `f`.
9. Operadores/`if` sobre closures são `Erro`; `0 ** -1` é `Erro`; resultado complexo nunca é aceito.
10. Erros léxicos/sintáticos chegam a `executar_programa` como `Erro` (não exceção).

Mensagens só são verificadas onde já aparecem nos seus testes: `divisão por zero`,
`aridade incorreta`, `condição do 'if' é uma função`, `esperava 'else'`, `esperava ';'`,
`tokens não consumidos`, `token desconhecido`.

## Deliberadamente fora do escopo (a especificação não define)

Comentários, parâmetros duplicados, recursão infinita/estouro de pilha, overflow de
`**`, precisão de inteiros gigantes, reuso das mesmas listas `env`/`store` entre chamadas.

## Validação feita

Cada valor esperado foi conferido contra uma implementação de referência independente
escrita só a partir do README (não é a sua). Além disso, 31 variações defeituosas dela
(escopo dinâmico, env mutável, `**` associativo à esquerda, `//`, avaliação da direita
para a esquerda, params compartilhados, etc.): os testes novos detectam 30 (o restante é
equivalente); os 34 testes originais detectavam apenas 6.
