# Listão de Exercícios — Estágios 1 a 3 (Aulas 01 a 08)

**Paradigmas de Linguagens de Programação — Ciência da Computação (UFCG) — 2026.2**

Esta lista cobre todo o conteúdo visto nas oito primeiras aulas, organizado pelos estágios do curso:

| Estágio | Tema | Aulas |
|---|---|---|
| 1 | Aritmética em RPN: pipeline, tratamento de erros, metalinguagens e especificação formal | 1–2 |
| 2 | Sintaxe estruturada: ASTs, s-expressões, BNF/EBNF, parsers, precedência e associatividade | 3–6 |
| 3 | Semântica de avaliação (big-step), operações totais, variáveis e ambientes | 7–8 |

---

## Como usar esta lista

- **É um guia de estudo.** Use-a como roteiro de revisão: se você consegue resolver as questões de um bloco sem consultar as notas, domina aquele bloco.
- **As mini-linguagens (`rpn`, `mlisp`, `calc`, `aljabr`) não são o ponto.** O que importa são os conceitos, as técnicas e as decisões de design por trás delas. Muitas questões pedem que você reaplique uma ideia a uma linguagem ou a um operador *diferente* do que foi visto em aula, de propósito.
- **Python é a metalinguagem.** Todas as questões de implementação são em Python. Você não precisa partir do código feito em sala; na verdade, é mais proveitoso reescrevê-lo por conta própria.
- **Escreva testes.** Em toda questão de implementação, inclua casos de teste de sucesso *e* de erro (léxico, sintático e semântico).
- **Pense em alternativas.** Sempre que possível, pergunte-se: que outra decisão de design poderia ter sido tomada aqui, e o que ela implicaria?
- **Estas questões devem ser usadas nas provas.** Farei as provas a partir de questões obtidas destas listas. Então, estude-as.

> Reforçando. Use estes exercícios como apoio pra estudar. Estude o conteúdo
> das aulas (os README.md de cada aula) e use os exercícios nesta lista
> referentes àquela aula para se auto-avaliar. Ao final, há ainda questões
> integradoras dos conteúdos. Você talvez queira dar uma olhada nessas questões
> antes, já que elas requerem uma visão do conjunto do curso.

### Legenda dos tipos de questão

| Marca | Tipo | O que se espera |
|---|---|---|
| `[C]` | Conceitual | Resposta em texto, com suas próprias palavras e exemplos |
| `[P]` | Papel e lápis | Traços, derivações, árvores, transformações, cálculos à mão |
| `[I]` | Implementação | Código Python com testes |
| `[D]` | Depuração / análise | Encontrar e explicar defeitos em código, regex ou especificações |
| `[X]` | Desafio | Questão mais aberta ou mais difícil; opcional |

### Mapa das aulas

| Aula | Tema | Blocos |
|---|---|---|
| 1 | RPN, notações, tabela de rastreamento, pipeline | 1A, 1B |
| 2 | Tratamento de erros, metalinguagens, léxico/sintaxe/semântica formais | 1C, 1D |
| 3 | Sintaxe concreta × abstrata, AST, s-expressões | 2A, 2B |
| 4 | Léxico e BNF formais, parser descendente recursivo | 2C, 2D |
| 5 | EBNF, aridade, associatividade, precedência, projeto da gramática de `calc` | 2E, 2F |
| 6 | Transformações de gramáticas, recursão à esquerda, parser LL(1) de `calc` | 2G |
| 7 | Lexer renovado, semântica operacional big-step de `calc` | 3A, 3B |
| 8 | `calc` com unários e operações totais; `aljabr` (variáveis e `let..in`) | 3C, 3D |

Ao final há ainda um bloco de **questões integradoras** (Estágios 1 a 3).

---

# Estágio 1 — Aritmética em RPN (Aulas 1 e 2)

### Ao final deste estágio você deve ser capaz de

- converter expressões entre as notações infixa, prefixa e posfixa, e avaliá-las;
- simular a avaliação de RPN com uma tabela de rastreamento e explicar o papel da pilha como *estado da computação*;
- implementar um interpretador RPN e organizá-lo em lexer, parser e interpretador, explicando a responsabilidade de cada etapa e o tipo de erro detectado em cada nível;
- tratar erros de forma monádica, entendendo erros como *possíveis significados* de programas;
- distinguir linguagem-objeto de metalinguagem e discutir vantagens e limites de linguagem natural, implementação de referência e notações formais;
- especificar o léxico com expressões regulares, a sintaxe com BNF e a semântica com regras de transição, e derivar programas a partir de uma gramática.

---

## 1A — Notações e avaliação de expressões (Aula 1)

**1.1** `[C]` Defina notação infixa, notação polonesa (prefixa) e notação polonesa reversa (posfixa). Para cada uma, diga onde fica o operador e se a notação precisa de parênteses ou de regras de precedência para ser não ambígua. Por quê?

**1.2** `[P]` Escreva `(b ** 2) - ((4 * a) * c)` e `3 * (1 + 2)` nas notações prefixa e posfixa.

**1.3** `[P]` Converta cada expressão RPN abaixo para infixa totalmente parentizada e calcule seu valor.

- `5 1 2 + 4 * + 3 -`
- `1 2 3 4 + + +`
- `1 2 + 3 + 4 +`
- `1 2 3 + 4 * -`
- `8 2 / 3 - 2 *`

**1.4** `[P]` Converta cada expressão infixa abaixo para RPN (aplique as regras usuais de precedência e associatividade à esquerda).

- `(1 + 2) * (3 + 4)`
- `10 - (2 - 3)`
- `10 - 2 - 3`
- `2 * 3 + 4 * 5`

**1.5** `[C]` Explique por que a RPN dispensa parênteses e regras de precedência. Para ilustrar, dê duas expressões infixas que diferem apenas pelos parênteses (por exemplo, `(1 + 2) * 3` e `1 + (2 * 3)`) e mostre que suas versões em RPN diferem apenas pela *ordem dos tokens*.

**1.6** `[P]` Avalie as expressões abaixo por *simplificações sucessivas* (uma sequência de expressões equivalentes, como feito em aula). Em que sentido a última expressão da sequência é o "significado" da primeira?

- `7 2 3 * - 4 +`
- `15 7 1 1 + - / 3 *`

**1.7** `[P]` Construa a *tabela de rastreamento* (colunas: pilha e restante da expressão; topo da pilha à direita) para cada programa.

- `4 12 3 / +`
- `2 3 4 * + 5 -`
- `5 1 2 + 4 * + 3 -`

**1.8** `[C]` Considere o programa RPN `10 4 -`.

- (a) Quando o operador `-` é lido, que valor está no topo da pilha?
- (b) Qual valor é desempilhado primeiro e qual operando da subtração ele representa?
- (c) Se o interpretador calculasse `v1 - v2`, com `v1` sendo o primeiro valor desempilhado, qual resultado produziria? Por quê está errado?
- (d) Isso é um problema para `+` e `*`? E para `/` e `**`?

**1.9** `[C]` Compare as duas formas de avaliar RPN vistas em aula (simplificações sucessivas × tabela de rastreamento). Que estrutura de dados representa o estado da computação em cada uma? Por que a segunda é mais adequada para escrever um interpretador?

**1.10** `[P]` Faça a tabela de rastreamento, até onde for possível, de cada programa abaixo. Diga em que estado o processamento termina ou trava e justifique por que o programa não tem um valor.

- `1 +`
- `1 2`
- `1 2 3 +`
- `+`
- (programa vazio)

**1.11** `[I]` Sem consultar o código de aula, implemente `avaliar(programa: str) -> int` para RPN com os operadores `+`, `-`, `*` e `/`, usando uma lista como pilha. Teste com os programas dos exercícios 1.3, 1.6 e 1.7. (Por enquanto, os programas de 1.10 podem simplesmente levantar exceções.)

**1.12** `[C]` Por que não é possível usar o mesmo símbolo `-` para subtração (binária) e para negação (unária) em RPN? Proponha duas soluções de design diferentes e compare-as. (Dica: o que o interpretador sabe sobre o programa no momento em que lê o token `-`?)

**1.13** `[I]` Estenda seu interpretador RPN com os operadores `**` e `%` e com um operador **ternário** (por exemplo, `x min max clamp`, que limita `x` ao intervalo `[min, max]`). Para cada extensão, liste o que precisou mudar: o léxico? a sintaxe? a semântica? Por que operadores de aridades diferentes exigem mais cuidado?

**1.14** `[X]` Acrescente os operadores `dup` (duplica o topo), `swap` (troca os dois valores do topo) e `drop` (descarta o topo). O que eles revelam sobre a pilha como "estado da computação"? Que construções a notação BNF e as regras de transição precisariam ganhar para descrevê-los?

---

## 1B — O pipeline de processamento: léxico, sintaxe e semântica (Aulas 1 e 2)

**1.15** `[C]` Descreva o pipeline de processamento de uma linguagem de programação: *código fonte → lexer → tokens → parser → programa validado → interpretador → resultado*. Para cada etapa, diga qual é a entrada, qual é a saída, qual é a sua responsabilidade e que tipo de erro ela detecta.

**1.16** `[C]` Classifique cada programa RPN abaixo como: *erro léxico*, *erro sintático*, *erro semântico (de execução)* ou *sem erro*. Justifique.

- `1 2 +`
- `1 + 2`
- `1 2 &`
- `3 0 /`
- `1 2 3`
- `+ 1 2`
- `12 x +`
- `1 2 + +`

**1.17** `[C]` Por que, em geral, não faz sentido iniciar a análise sintática de um programa que contém erro léxico? E por que não faz sentido interpretar um programa com erro sintático?

**1.18** `[C]` Por que "interpretar um programa" é, na prática, sinônimo de "executar um programa"? O que significa atribuir um *significado* a um programa?

**1.19** `[C]` Qual a diferença entre *lexer* e *tokenizador*? Por que falamos em *tokens*, e não em "palavras"?

**1.20** `[C]` Na primeira versão do interpretador RPN, lexer e parser praticamente não existiam como funções separadas. Por que isso foi possível? Por que, mesmo assim, o curso insiste em separar as três etapas?

**1.21** `[I]` Refatore seu interpretador RPN em três funções independentes — `tokenizador`, `parser` e `interpretador` — de modo que cada uma detecte apenas os erros do seu nível.

**1.22** `[I]` Em aula, as constantes `OPERADORES` e `OPERACAO` surgiram de um refatoramento.

- (a) Explique o papel de cada uma (qual aspecto da linguagem — léxico, sintaxe ou semântica — cada uma sustenta?).
- (b) Acrescente o operador `//` (divisão inteira) mudando *apenas* essas constantes. O que prova que isso funcionou?
- (c) Que operador *não* poderia ser acrescentado só mexendo nessas constantes? Por quê?

---

## 1C — Tratamento de erros (Aula 2)

**1.23** `[D]` Monte uma bateria de testes com ao menos 10 programas RPN inválidos (pelo menos três de cada tipo: léxico, sintático e semântico). Rode-os em uma versão do seu interpretador que usa `raise` e descreva o que acontece com a execução.

**1.24** `[C]` Explique o *tratamento monádico de erro* usado no curso. O que significa dizer que "erros são possíveis significados de programas"? Compare essa abordagem com `try..except` quanto à estrutura do código `main` e ao caminho que o erro percorre.

**1.25** `[I]` Defina o tipo `Erro` (um alias de `str`) e o decorador `monadic_error`. Aplique-o ao `parser` e ao `interpretador`. Explique, linha a linha, o que faz a função `wrapper`.

**1.26** `[D]` O tipo `Erro` como alias de `str` tem uma limitação apontada em aula. Qual é? Em que situação ele deixaria de funcionar? Proponha e implemente uma versão baseada em classe que elimine o problema.

**1.27** `[P]` Mostre, passo a passo, quais funções do pipeline são efetivamente executadas (e com quais argumentos) quando o `tokenizador` devolve um `Erro`. O `parser` e o `interpretador` chegam a executar seus corpos?

**1.28** `[C]` Compare quatro estratégias de tratamento de erros: exceções, códigos de retorno, valor especial (monádico) e `Optional`/`Result`. Cite vantagens, desvantagens e pelo menos uma linguagem real que adote cada uma. *(Pesquisa.)*

---

## 1D — Metalinguagens e especificação formal (Aula 2)

**1.29** `[C]` Defina *linguagem-objeto* e *metalinguagem*. No caso de RPN, identifique a linguagem-objeto e todas as metalinguagens usadas até aqui, dizendo qual papel cada uma desempenha.

**1.30** `[C]` Discuta as vantagens e desvantagens de especificar uma linguagem (a) apenas em linguagem natural; (b) apenas por um interpretador em Python; (c) pela combinação das duas. Qual a diferença entre o interpretador ser *a especificação* e ser *uma implementação* da linguagem?

**1.31** `[C]` Um colega quer implementar RPN em Java tomando o seu interpretador Python como única referência. Que problemas ele pode enfrentar? Como uma especificação formal ajudaria?

**1.32** `[P]` O alfabeto de RPN é `0`–`9`, `+`, `-`, `*`, `/` e espaço. Dê cinco sequências de caracteres que são tokens válidos e cinco que usam apenas caracteres do alfabeto mas **não** são tokens.

**1.33** `[P]` Sobre expressões regulares:

- (a) Leia `NÚMERO ::= DÍGITO DÍGITO*` e explique quais operações de expressões regulares aparecem (união, concatenação, iteração).
- (b) Por que `NÚMERO ::= DÍGITO*` está errada? Que string indesejada ela aceita?
- (c) Escreva expressões regulares para: números inteiros com sinal opcional; números decimais como `3.14`; identificadores formados por letras, dígitos e `_`, que não comecem com dígito.
- (d) Que tokens as regex `[0-9]+` e `\s+` reconhecem? Por que o espaço é tratado como uma categoria léxica à parte?

**1.34** `[C]` Se o léxico de RPN passasse a aceitar números com sinal (como `-5`), surgiria uma ambiguidade com o operador `-`. Mostre uma entrada ambígua (por exemplo, `3 -5 +`) e discuta como um projetista poderia resolver o problema.

**1.35** `[P]` Leia a regra `<expr-rpn> ::= NÚMERO | <expr-rpn> <expr-rpn> OPERADOR`. Explique por que ela é *recursiva* e explique em português as duas garantias que uma gramática oferece: (1) todo programa derivável é válido; (2) todo programa válido é derivável.

**1.36** `[P]` Mostre uma derivação (a cada passo, expandindo o não-terminal mais à esquerda) para cada programa.

- `3 4 + 5 *`
- `1 2 3 + +`
- `5 1 2 + 4 * + 3 -`

**1.37** `[P]` Justifique, usando a gramática, por que `1 +` e `1 2` **não** podem ser derivados a partir de `<expr-rpn>`.

**1.38** `[C]` Explique os termos *terminal*, *não-terminal*, *categoria léxica*, *categoria sintática*, *regra de produção* e *derivação*. Como a especificação léxica (expressões regulares) se articula com a especificação sintática (BNF)?

**1.39** `[P]` Escreva em BNF:

- (a) a gramática de RPN estendida com um operador unário pós-fixo `neg`;
- (b) a gramática de expressões em notação **prefixa** com operadores binários. Compare-a com a de RPN.

**1.40** `[P]` Leia a regra de transição `⟨N · restante, pilha⟩ → ⟨restante, N :: pilha⟩`. O que significam os meta-operadores `·` e `::`? Escreva as regras de transição para `-`, `*` e `/` (atenção à ordem dos operandos!). Por que o `+` do lado esquerdo da regra de soma e o `+` do lado direito não são o mesmo símbolo?

**1.41** `[P]` Aplique as regras de transição ao programa `2 3 4 * +`, a partir do estado inicial `⟨programa, []⟩`, listando cada estado e a regra usada.

**1.42** `[P]` Defina, nas regras de transição, quando uma computação termina com *sucesso* e qual é o seu significado. Para `1 2` e `1 +`, mostre em que estado a computação trava (não há regra aplicável) e por que o significado do programa é um erro.

**1.43** `[C]` Uma mesma semântica de RPN foi dada de três formas: texto + código Python, tabela de rastreamento e regras de transição. Relacione as três: o que cada uma mostra com clareza e o que cada uma esconde?

**1.44** `[C]` O que é o *estado* da computação em RPN? Por que as regras de transição são chamadas de semântica *de pequenos passos*?

**1.45** `[X]` Escreva as regras de transição para `neg`, `dup`, `swap` e `drop`. Há alguma situação em que a regra não se aplica? O que isso diz sobre o significado do programa?

**1.46** `[C]` A sintaxe de RPN foi projetada para facilitar a interpretação por uma pilha. Que benefícios isso traz para quem implementa a linguagem? Que custo traz para quem a usa?

**1.47** `[C]` *(Pesquisa.)* Que linguagens e dispositivos reais usam RPN ou uma máquina de pilha (por exemplo, Forth, PostScript, o bytecode da JVM, calculadoras HP)? Por que a escolha de uma pilha faz sentido em cada caso?

---
# Estágio 2 — Sintaxe estruturada: ASTs, s-expressões e notação infixa (Aulas 3 a 6)

### Ao final deste estágio você deve ser capaz de

- distinguir sintaxe concreta de sintaxe abstrata e representar a segunda por uma AST (árvore de sintaxe abstrata);
- relacionar os percursos em árvore (pré-ordem, em-ordem, pós-ordem) com as notações prefixa, infixa e posfixa;
- explicar por que uma s-expressão é uma AST escrita em forma textual e implementar um parser de s-expressões (por pareamento de parênteses);
- especificar léxico (expressões regulares) e sintaxe (BNF e EBNF) de uma linguagem, derivar programas a partir de uma gramática e raciocinar sobre ambiguidade;
- derivar mecanicamente um parser descendente recursivo LL(1) a partir de uma gramática, usando `peek` e `expect`;
- explicar aridade, associatividade e precedência como decisões de design, e codificá-las na estrutura de uma gramática;
- aplicar transformações de gramáticas (eliminação de produções vazias, eliminação de recursão à esquerda, fatoração à esquerda) preservando a linguagem gerada;
- explicar por que a recursão à esquerda impede o parser descendente recursivo e como o *folding* recupera a associatividade;
- projetar, implementar e testar o parser da linguagem `calc` (infixa), produzindo a mesma AST das notações anteriores.

---

## 2A — Sintaxe concreta × sintaxe abstrata e ASTs (Aula 3)

**2.1** `[C]` Defina *sintaxe concreta* e *sintaxe abstrata*. Que estrutura de dados costuma representar cada uma (lista de tokens, AST etc.)? Que informações do texto do programa aparecem na primeira e **não** aparecem na segunda?

**2.2** `[C]` Dê um exemplo de dois programas com sintaxes concretas diferentes que compartilham a mesma AST. Dê também um exemplo de uma sintaxe concreta que admite mais de uma AST possível. Que nome damos a esse segundo fenômeno?

**2.3** `[P]` Desenhe a AST de cada expressão. Nas ASTs, os parênteses aparecem? Por quê?

- `1 2 +`
- `1 2 3 * +`
- `1 + 2 * 3`
- `(1 + 2) * 3`
- `2 * (3 + 4) - 5`
- `(b ** 2) - ((4 * a) * c)`

**2.4** `[P]` Escreva a AST de cada item do exercício anterior como listas aninhadas de Python (`["+", 1, ["*", 2, 3]]`) e o caminho inverso: desenhe as árvores correspondentes às listas abaixo.

- `["-", ["*", 2, ["+", 3, 4]], 5]`
- `["+", ["+", 1, 2], 3]`
- `["+", 1, ["+", 2, 3]]`
- `["/", ["-", 10, 4], ["*", 1, 3]]`

**2.5** `[P]` Para cada uma das ASTs do exercício 2.4, produza os percursos **pré-ordem**, **pós-ordem** e **em-ordem** (neste último, reinserindo os parênteses necessários). Qual notação cada percurso produz? Por que o percurso em-ordem precisa de parênteses e os outros dois não?

**2.6** `[C]` "Em geral, ao construir interpretadores, queremos o caminho inverso: partir da sintaxe concreta e produzir a sintaxe abstrata." Explique, com suas palavras, qual é o papel do parser nesse caminho e por que ele é mais difícil que o percurso da árvore.

**2.7** `[P]` Mostre que as expressões `2 * (3 + 4)` (infixa), `(* 2 (+ 3 4))` (s-expressão) e `2 3 4 + *` (RPN) produzem a **mesma AST**. Desenhe a árvore uma única vez e mostre como cada sintaxe concreta é obtida a partir dela. O que isso sugere sobre a independência entre sintaxe e semântica?

**2.8** `[C]` Explique por que o interpretador recursivo sobre a AST é "extremamente simples". Qual propriedade da estrutura da AST se reflete diretamente na estrutura do código do interpretador?

**2.9** `[P]` Em que ordem os nós da AST abaixo são visitados pelo interpretador recursivo, e que valor cada nó produz? Compare com o percurso pós-ordem.

```
["+", ["*", 2, 3], ["-", 7, ["/", 8, 2]]]
```

**2.10** `[I]` Implemente `interpretador(ast) -> int | Erro` seguindo o pseudo-código recursivo de aula (nó folha devolve o próprio valor; nó interno avalia os operandos e aplica a operação de `OPERACAO`). Trate de forma monádica pelo menos: divisão por zero, operador desconhecido, nó mal formado (quantidade errada de operandos).

**2.11** `[I]` Escreva três funções que recebem uma AST e devolvem uma *string*: `para_prefixa`, `para_posfixa` e `para_infixa` (esta última totalmente parentizada). Teste com as ASTs dos exercícios 2.3 e 2.4.

**2.12** `[X]` Melhore `para_infixa` para escrever o **mínimo de parênteses necessários**, considerando precedência e associatividade usuais. Que informação a função precisa ter sobre cada operador para decidir?

**2.13** `[I]` Escreva funções recursivas sobre ASTs: `tamanho(ast)` (número de nós), `altura(ast)`, `folhas(ast)` (lista das folhas, da esquerda para a direita) e `contar(ast, op)` (quantas vezes um operador aparece).

**2.14** `[I]` Reescreva o parser de RPN para que, em vez de avaliar a expressão, ele **construa a AST**, usando uma pilha de subárvores. Em seguida, reaproveite o `interpretador` do exercício 2.10. Que erros sintáticos o seu parser detecta (e em que momento)?

**2.15** `[C]` Compare os dois caminhos para executar um programa RPN: (a) avaliar diretamente com a pilha de valores; (b) construir uma AST e depois interpretá-la. Quais as vantagens de cada um? Por que o segundo se torna indispensável em linguagens mais complexas?

---

## 2B — S-expressões e o algoritmo de pareamento de parênteses (Aulas 3 e 4)

**2.16** `[C]` O que é uma *s-expressão*? Qual a diferença entre ela e a notação polonesa (prefixa)? Por que ela dispensa regras de precedência?

**2.17** `[P]` Converta para s-expressões:

- `1 + 2 * 3`
- `(1 + 2) * 3`
- `(b ** 2) - (4 * a * c)`
- `1 + 2 + 3 + 4`

**2.18** `[P]` Desenhe a AST de cada s-expressão e diga quantos nós internos e quantas folhas ela tem. Existe relação entre o número de nós internos e o número de pares de parênteses?

- `(+ 1 (* 2 3))`
- `(- (* 2 3) (/ 8 4))`
- `(+ 1 2 3 4)`
- `(+ 2 (* 3 (- 4 1)) (/ 8 2))`

**2.19** `[C]` Explique a afirmação: "uma s-expressão *é*, literalmente, uma AST escrita em forma textual". O que cada par de parênteses indica? O que aparece logo depois do parêntese de abertura? O que acontece quando um argumento é um inteiro e quando começa com `(`?

**2.20** `[C]` *(Pesquisa.)* Lisp foi criada em 1958. Pesquise o termo *homoiconicidade* e relacione-o com a afirmação do exercício anterior. Que consequências práticas essa propriedade tem para quem escreve programas que manipulam programas?

**2.21** `[P]` Aplique o algoritmo de pareamento **por contador** às sequências abaixo, mostrando o valor do contador a cada token. Diga em que ponto (se algum) o algoritmo detecta falha e qual o tipo de falha (`)` sem `(` correspondente, ou `(` não fechado).

- `(()())`
- `(()`
- `())(`
- `)(`
- `((())`

**2.22** `[P]` Mostre que o pareamento por contador não é suficiente quando há mais de um tipo de delimitador, usando `([)]`. Em seguida, aplique o algoritmo com **pilha** e mostre como ele detecta o problema.

**2.23** `[I]` Implemente (a) o pareamento de parênteses por contador e (b) o pareamento por pilha para os delimitadores `()`, `[]` e `{}`. Teste com `{[()]}`, `([)]`, `((`, `}`.

**2.24** `[C]` O parser de s-expressões do curso usa pilha em vez de contador. Que informação adicional a pilha nos permite manter? Como ela é usada para construir a AST?

**2.25** `[P]` Execute à mão o algoritmo do parser com pilha sobre `(+ 1 (* 2 3))`. Mostre, após cada token, o conteúdo da pilha e a AST parcial em construção.

**2.26** `[D]` O pseudo-código visto em aula trata apenas s-expressões corretas. Para cada entrada abaixo, descreva o que acontece com aquele pseudo-código e que erro sintático deveria ser reportado.

- (lista de tokens vazia)
- `+ 1 2`
- `(+ 1 2`
- `(+ 1 2))`
- `(+ 1 2) (* 3 4)`
- `()`
- `(1 2 3)`
- `(+ (* 2 3)`

**2.27** `[I]` Implemente o parser de s-expressões com pilha **detectando todos os erros do exercício anterior** e devolvendo `Erro` com mensagens úteis. Escreva testes para cada caso.

**2.28** `[I]` (*mlisp-v2*) Evolua o interpretador de s-expressões para suportar operadores com **aridades diferentes**, incluindo operações **variádicas** (por exemplo, `(+ 1 2 3 4)`).

- (a) Decida e documente a semântica dos casos de borda: `(+)`, `(*)`, `(- 5)`, `(- 10 2 3)`, `(/ 8)`, `(/ 100 5 2)`.
- (b) Cada decisão é uma escolha de *design*. Justifique-as (por exemplo, o elemento neutro).
- (c) Que partes da implementação precisaram mudar: léxico, sintaxe ou semântica?

**2.29** `[I]` (*entrada de dados*) Acrescente a mlisp um átomo `?` que, ao ser avaliado, lê um inteiro da entrada padrão.

- (a) Em que nível (léxico, sintático, semântico) a mudança foi feita?
- (b) Avalie `(- ? ?)` com a entrada `10` e depois `3`. A ordem de avaliação dos argumentos agora é *observável*? Isso já era assim antes?
- (c) O que isso sugere sobre a propriedade de a semântica ser uma função apenas da AST?

**2.30** `[C]` Compare o esforço de escrever o parser de RPN, o de s-expressões e o de notação infixa. Que decisão de design de cada sintaxe explica a diferença?

---

## 2C — Léxico e sintaxe formais de mlisp (Aula 4)

**2.31** `[P]` Para mlisp, o léxico tem quatro categorias: `LPAREN`, `RPAREN`, `OPERADOR` e `INTEIRO`. Escreva uma expressão regular para cada uma. Em seguida, classifique cada token de `(+ 12 (* 3 4))`.

**2.32** `[C]` Explique os termos *categoria léxica* e *terminal*. Por que o mesmo conceito recebe dois nomes? Em que contexto cada nome é usado?

**2.33** `[D]` Um aluno definiu `OPERADOR ::= [+-*/]`. Em Python, `re.compile(r"[+-*/]")` falha. Por quê? Corrija a expressão de duas maneiras diferentes.

**2.34** `[P]` Escreva expressões regulares para: inteiros com sinal opcional; números decimais como `3.14`; identificadores (letras, dígitos e `_`, sem começar por dígito); comentários de linha iniciados por `#`. Para cada uma, dê três cadeias aceitas e três rejeitadas.

**2.35** `[C]` Suponha que mlisp passe a aceitar números negativos como `-5`. Surge uma ambiguidade léxica com o operador `-`. Mostre uma entrada ambígua e discuta duas soluções de design (uma tratada no léxico, outra na sintaxe). Em mlisp, o contexto sintático ajuda a decidir? Por quê?

**2.36** `[P]` A gramática de mlisp é:

```
<s-expressão>  ::=  LPAREN OPERADOR <argumentos> RPAREN
<argumentos>   ::=  <arg> <argumentos> | ε
<arg>          ::=  INTEIRO | <s-expressão>
```

Indique os terminais, os não-terminais e o símbolo inicial. Em seguida, derive (sempre expandindo o não-terminal mais à esquerda, indicando a produção usada):

- `(+ 2 (* 3 4))`
- `(* (+ 1 2) 3 (- 5))`
- `(+)`

**2.37** `[P]` Desenhe a árvore de derivação de `(+ 2 (* 3 4))`. Compare-a com a AST da mesma expressão: que nós desaparecem e por quê?

**2.38** `[C]` A gramática de mlisp aceita cada cadeia abaixo? Justifique observando o símbolo inicial e as regras.

- `(+)`
- `(+ 1 (2))`
- `((+ 1 2))`
- `(+ 1 2) 3`
- `42`
- `(+ 1 (* 2 3) 4)`

**2.39** `[P]` Modifique a gramática de mlisp para que:

- (a) um inteiro isolado também seja um programa válido;
- (b) todo operador exija **pelo menos um** argumento;
- (c) todo operador exija **pelo menos dois** argumentos;
- (d) o átomo `?` (entrada de dados) possa aparecer como argumento.

Para cada modificação, diga se mudou o léxico ou a sintaxe.

**2.40** `[C]` Explique, com suas palavras, as duas garantias de uma gramática: (1) toda derivação produz um programa válido; (2) todo programa válido tem uma derivação. O que significa dizer que um texto é "sintaticamente incorreto"?

**2.41** `[C]` Defina gramática *ambígua*. A gramática de mlisp é ambígua? Argumente. Por que a ambiguidade é indesejável em uma linguagem de programação?

**2.42** `[P]` Projete (léxico e sintaxe em BNF) uma linguagem de expressões lógicas em notação **prefixa** com `and`, `or`, `not`, `true` e `false` (por exemplo, `(and true (not false))`). Derive um programa e desenhe a AST.

**2.43** `[X]` Tente escrever uma expressão regular que reconheça exatamente as sequências de parênteses balanceados. O que acontece? O que a BNF tem que as expressões regulares não têm e que explica por que usamos cada uma para um nível da linguagem?

**2.44** `[C]` Por que não basta a intuição para construir lexers e parsers de linguagens reais? Qual o papel das especificações formais na construção desses componentes?

---

## 2D — Parser descendente recursivo (Aulas 4 e 5)

**2.45** `[C]` Explique a correspondência entre uma gramática BNF e um parser descendente recursivo: o que vira cada não-terminal, cada sequência, cada alternativa `B | C`, cada produção vazia, cada recursão e cada terminal.

**2.46** `[C]` Diferencie `expect(T)` de `peek(T)`. Por que o `peek` é necessário? O que daria errado se `parse_arg` consumisse o token antes de decidir qual produção aplicar?

**2.47** `[C]` O que significa uma gramática (e um parser) ser **LL(1)**? O que significam as duas letras "L"? Mostre, para mlisp, qual token decide a escolha em cada ponto de decisão (`parse_argumentos` e `parse_arg`).

**2.48** `[I]` Implemente uma classe `Stream` com os métodos `next()` e `peek()`, e as funções `expect(stream, categoria)` e `peek(stream, categoria)`. Em seguida, derive **mecanicamente** o parser de mlisp a partir da BNF (`parse_s_expressao`, `parse_argumentos`, `parse_arg`), com tratamento monádico de erros.

**2.49** `[D]` O código abaixo deveria implementar `parse_argumentos`. Há um defeito. Qual? Para que entradas ele se manifesta? Corrija.

```python
def parse_argumentos(stream):
    """<argumentos>  ::=  <arg> <argumentos> | ε"""
    if RPAREN(stream.peek()):
        return []

    erro = arg = parse_arg(stream)
    if isinstance(erro, Erro):
        return erro

    erro = argumentos = parse_arg(stream)
    if isinstance(erro, Erro):
        return erro

    return [arg] + argumentos
```

**2.50** `[I]` Seu parser aceita `(+ 1 2` ? Aceita `(+ 1 2))`? Aceita `(+ 1 2) 3`? Trate o fim prematuro da entrada (o `next()` devolve `None`) e verifique que, depois do programa, não restam tokens.

**2.51** `[I]` Melhore as mensagens de erro do parser: indique a **posição** do token problemático e compare *esperado* × *encontrado*. Escreva testes para pelo menos cinco erros sintáticos distintos.

**2.52** `[C]` O código de aula usa atribuição encadeada (`erro = arg = parse_arg(stream)`) e o operador *walrus* (`:=`). Explique o que cada um faz e reescreva um trecho sem eles.

**2.53** `[P]` Derive o pseudo-código do parser para a gramática abaixo (listas aninhadas como `[1, [2, 3], []]`). Em seguida, implemente-o.

```
<lista>  ::=  LCOL <itens> RCOL
<itens>  ::=  <item> <resto> | ε
<resto>  ::=  VIRGULA <item> <resto> | ε
<item>   ::=  INTEIRO | <lista>
```

**2.54** `[P]` Escreva o léxico (expressões regulares) e a gramática BNF de uma linguagem de **atribuições simples**, como `x = 3; y = x + 1;`. Em seguida, derive o parser descendente recursivo correspondente. Que decisões de design você teve de tomar?

**2.55** `[C]` Diferencie *erro léxico* e *erro sintático* no contexto do parser: dê dois exemplos de cada tipo em mlisp e diga qual etapa do pipeline deve reportá-los.

---

## 2E — EBNF, aridade, associatividade e precedência (Aula 5)

**2.56** `[C]` Quais elementos a EBNF acrescenta à BNF? Explique `X+`, `X*`, `( … )`, `[ … ]` e `{ … }`. Que vantagens a EBNF traz para a leitura da gramática e para a implementação do parser?

**2.57** `[P]` Escreva a gramática de mlisp com uma única regra em EBNF e converta cada parte em um trecho de código do parser (identifique o `while` e os `if`s). Compare com a versão em BNF: quantas funções cada uma exige?

**2.58** `[P]` Converta as regras EBNF abaixo para BNF pura (podendo criar regras auxiliares):

- `A ::= b [ c ] d`
- `A ::= { x | y }`
- `A ::= x { y } z`
- `A ::= ( x | y )+`

**2.59** `[P]` Descreva em português a linguagem definida por cada regra e dê três cadeias que pertencem e duas que não pertencem a ela.

- `S ::= a { b } c`
- `S ::= [ a ] b+`
- `S ::= ( a | b ) { c }`

**2.60** `[P]` Escreva em EBNF: (a) uma lista (possivelmente vazia) de inteiros separados por vírgula; (b) a gramática de listas aninhadas do exercício 2.53 em uma única regra; (c) a gramática de mlisp com argumentos opcionais.

**2.61** `[I]` Implemente o parser de mlisp a partir da regra EBNF única (com laço `while`). Teste-o com a mesma bateria de testes dos exercícios 2.48 e 2.50.

**2.62** `[C]` Por que a notação infixa **exige** operações binárias? Como se escreve em `calc` o equivalente a `(+ 1 2 3 4)`? Que nova questão aparece quando se encadeiam operações?

**2.63** `[C]` Defina **associatividade** e **precedência**. Qual das duas é propriedade de *cada operador* e qual é propriedade da *relação entre operadores*? Por que ambas são decisões de design e não propriedades "naturais"?

**2.64** `[C]` Para cada operador de `calc` (`+`, `-`, `*`, `/`, `**`), explique por que a associatividade importa ou não para o resultado. Por que a escolha usual é associatividade à esquerda para `-` e `/`, e à direita para `**`?

**2.65** `[P]` Desenhe as duas ASTs possíveis de cada expressão e calcule o valor de cada uma. Qual delas a linguagem deve produzir, segundo as convenções adotadas no curso?

- `10 - 4 - 3`
- `100 / 10 / 5`
- `2 ** 3 ** 2`
- `2 + 3 + 4`

**2.66** `[P]` Aplicando as precedências e associatividades de `calc`, desenhe a AST e calcule o valor:

- `2 + 3 * 4 ** 2 / 8 - 1`
- `2 ** 3 ** 2 * 2`
- `1 - 2 - 3 - 4`
- `(1 + 2) * 3 ** 2`

**2.67** `[C]` Por que `rpn` e `mlisp` não precisaram de regras de precedência nem de associatividade? Quem tomava essas decisões nessas linguagens?

**2.68** `[C]` Parênteses: em mlisp são obrigatórios; em `calc` são opcionais e servem para forçar a ordem de avaliação. Por que o foco de `calc` está no programador da linguagem e não no implementador do interpretador? Os parênteses aparecem na AST? Por quê?

**2.69** `[C]` Imagine duas calculadoras: (a) todas as operações têm a mesma precedência e se agrupam da esquerda para a direita; (b) todas as operações se agrupam da direita para a esquerda (como em APL). Desenhe as ASTs de `2 + 3 * 4` em cada uma e escreva a gramática correspondente. O que isso mostra sobre o papel da gramática no design?

**2.70** `[X]` *(Pesquisa.)* Em Python, `a < b < c` tem um significado especial (encadeamento de comparações); em Java, é um erro de tipo. Que decisão de design de sintaxe e semântica explica essa diferença? Que outras linguagens tratam comparações como operadores **não associativos**?

---

## 2F — Projeto da gramática de `calc` (Aula 5)

**2.71** `[C]` Considere a gramática de uma só categoria de expressão:

```
exp ::= exp + exp | exp - exp | exp * exp | exp / exp | exp ** exp | INTEIRO | ( exp )
```

- (a) Mostre duas árvores de derivação distintas para `2 + 3 * 4` e duas para `2 ** 3 ** 4`.
- (b) Que propriedade ela garante (aridade) e quais ela não impõe?
- (c) Por que a AST final dependeria das "escolhas do parser"?

**2.72** `[P]` Com a gramática por níveis (segunda tentativa):

```
exp   ::= exp + termo | exp - termo | termo
termo ::= termo * fator | termo / fator | fator
fator ::= fator ** atomo | atomo
atomo ::= INTEIRO | ( exp )
```

- (a) Mostre que a precedência passa a ser imposta pela gramática.
- (b) Desenhe a derivação de `2 ** 3 ** 4` e mostre que o agrupamento é `(2 ** 3) ** 4`.
- (c) Por que esse agrupamento é inadequado para a exponenciação?

**2.73** `[P]` Explique o ajuste `fator ::= atomo ** fator | atomo`. Mostre que `2 ** 3 ** 4` agora é agrupado à direita e que a precedência **não** mudou.

**2.74** `[P]` Com a gramática final de `calc`, faça a derivação (indicando a produção usada em cada passo), desenhe a árvore de derivação e a AST de:

- `2 * 3 + 4`
- `2 * (3 + 4)`
- `2 ** 3 ** 2`
- `1 - 2 - 3`
- `(1)`
- `1 + 2 * 3 ** 4`

**2.75** `[C]` Explique como cada propriedade é codificada na gramática, ilustrando com uma regra de `calc`: (a) precedência; (b) associatividade; (c) aridade. Por que "uma gramática bem projetada faz com que a AST correta seja uma consequência natural das derivações"?

**2.76** `[C]` Diferencie árvore de derivação e AST. Para `2 * (3 + 4)`, indique quais nós e quais terminais desaparecem na AST e por quê.

**2.77** `[P]` O que muda se, em vez da regra escolhida, `fator` for definido como:

- (a) `fator ::= fator ** atomo | atomo`
- (b) `fator ::= atomo ** atomo | atomo`

Encontre expressões que produzam derivações diferentes nas gramáticas original e proposta. Alguma das alternativas passa a **rejeitar** programas antes válidos?

**2.78** `[P]` Modifique a gramática de `calc` para:

- (a) incluir `%` com a mesma precedência de `*` e `/`;
- (b) incluir `//` (divisão inteira) com a mesma precedência de `/`;
- (c) tornar `+` e `-` associativos à **direita** (`exp ::= termo + exp | termo - exp | termo`). Calcule `10 - 3 + 2` nas duas versões. O que isso mostra sobre associatividade de operadores que dividem o mesmo nível de precedência?

**2.79** `[P]` Projete a regra para um operador `==` **não associativo**, de precedência menor que `+`, de modo que `a == b == c` seja um erro sintático. Como a gramática expressa a proibição?

**2.80** `[X]` Acrescente a `calc` um condicional ternário `c ? a : b` com a menor precedência de todas e associativo à direita. Escreva a gramática e a AST de `1 ? 2 : 3 ? 4 : 5`.

**2.81** `[C]` Explique a observação: "ao escrever uma BNF, não estamos apenas descrevendo a forma textual da linguagem; estamos projetando a forma das ASTs".

**2.82** `[P]` Transforme as regras de `calc` para a notação EBNF, aproveitando `{ }` e `[ ]`. Explique o que mudou em cada regra e o que **perdeu** em termos de associatividade.

**2.83** `[P]` Explique por que a regra `A ::= A x | A y | z` pode ser reescrita como `A ::= z { x | y }`: (a) por que a regra é válida? (b) que benefício traz para o parser? Enumere as cadeias de comprimento até 3 geradas por ambas.

---

## 2G — Transformações de gramáticas e o parser LL(1) de `calc` (Aula 6)

**2.84** `[C]` Por que a recursão à esquerda (`exp ::= exp + termo | termo`) causa recursão infinita num parser descendente recursivo? Escreva a sequência de chamadas de `parse_exp` para qualquer entrada.

**2.85** `[C]` Mesmo que se contornasse a recursão infinita, ainda não seria possível escolher a produção de `exp` com um único token à frente. Por quê? Defina `PRIMEIRO` e explique por que a igualdade `PRIMEIRO(exp) = PRIMEIRO(termo)` impede a decisão. Por que nenhum `k` finito resolve?

**2.86** `[P]` Calcule `PRIMEIRO` de cada não-terminal:

- na gramática de `calc` (`exp`, `termo`, `fator`, `atomo`);
- na gramática de mlisp (`s-expressão`, `arg`, `argumentos`).

**2.87** `[P]` Para cada gramática, diga se a decisão de produção pode ser tomada com **um** token de *look-ahead*. Quando não puder, indique qual transformação resolve.

- `A ::= a B | b C`
- `A ::= a B | a C`
- `A ::= A a | b`
- `A ::= ( A ) | x`
- `A ::= B c | B d`, com `B ::= x`

**2.88** `[P]` *Eliminação de produções vazias.* Transforme, primeiro em BNF e depois em EBNF:

```
A ::= ε | a
B ::= b A c
```

Faça o mesmo com `L ::= ε | x L` e `S ::= a L b`. Por que produções vazias são "incômodas" e quando causam conflitos em um parser?

**2.89** `[P]` *Eliminação de recursão à esquerda.* Aplique a regra (`A ::= A x | A y | z  ⟹  A ::= z { x | y }`) a:

- `A ::= A x | y`
- `E ::= E + T | E - T | T`
- `L ::= L , I | I`
- `A ::= A a | A b | A c | d | e`

Em seguida, escreva a forma geral com `α₁ … αₘ` e `β₁ … βₙ`, identificando cada `α` e cada `β` nos exemplos.

**2.90** `[P]` Mostre, enumerando derivações, que `A ::= A x | A y | z` e `A ::= z { x | y }` geram as mesmas cadeias. Escreva também a versão em BNF pura (com regra auxiliar `A'`) e compare as três.

**2.91** `[P]` Refaça, passo a passo, os quatro passos do refatoramento da gramática de `calc` para `termo` e `fator`: (1) eliminar recursão à esquerda; (2) fatorar à esquerda; (3) introduzir agrupamento EBNF; (4) eliminar produções vazias. Chegue a `termo ::= fator { ( * | / ) fator }` e `fator ::= atomo [ ** fator ]`.

**2.92** `[P]` *Fatoração à esquerda.* Aplique a transformação em BNF e em EBNF:

- `S ::= if E then S | if E then S else S | outro`
- `A ::= a b c | a b d | a e | f`
- `fator ::= atomo ** fator | atomo`
- `Cmd ::= ID := Exp | ID ( Args )`

Por que o `parse_S` da primeira não é LL(1) antes da fatoração?

**2.93** `[X]` Depois da fatoração, `S ::= if E then S [ else S ] | outro` ainda deixa uma dúvida em `if E then if E then outro else outro`: a qual `if` pertence o `else`? Explique por que a gramática original era ambígua, como o parser descendente recursivo resolve a questão e que regra Java e C adotam.

**2.94** `[C]` Interprete as transformações de gramáticas como *refatoramentos de código*. Quais propriedades se preservam (linguagem gerada) e quais podem mudar (número de não-terminais, forma das árvores de derivação, a codificação da associatividade)?

**2.95** `[C]` Depois de eliminar a recursão à esquerda, a gramática deixa de garantir associatividade à esquerda. Como a repetição `{ … }` deve ser lida? O que é o *folding* e por que ele é uma *ação semântica* que deve ser implementada pelo parser (ou interpretador)?

**2.96** `[C]` Em que situações é legítimo gerar um nó n-ário (`Soma(2, 3, 4)`) em vez de nós binários? Por que isso seria incorreto para `-`, `/` e `**`? O que seria `Subtração(2, 3, 4)`?

**2.97** `[I]` Implemente o parser LL(1) de `calc` a partir da gramática EBNF final:

```
exp   ::= termo { ( + | - ) termo }
termo ::= fator { ( * | / ) fator }
fator ::= atomo [ ** fator ]
atomo ::= INTEIRO | ( exp )
```

- ASTs em listas aninhadas, `[op, esquerda, direita]`.
- `parse_exp` e `parse_termo` usam `while` com *folding* à esquerda; `parse_fator` usa recursão à direita.
- Teste: `2 + 3 + 4` deve produzir `["+", ["+", 2, 3], 4]` e `2 ** 3 ** 2` deve produzir `["**", 2, ["**", 3, 2]]`.
- Trate, monadicamente, parênteses não pareados, operando faltando, operador sobrando e *tokens* sobrando ao final.

**2.98** `[D]` Qual o defeito do código abaixo? Que AST ele produz para `10 - 3 - 2` e qual o valor calculado? Corrija.

```python
def parse_exp():
    termo = parse_termo()
    while peek() in ['+', '-']:
        op = expect(TOKEN)
        termo2 = parse_termo()
        termo = [op, termo2, termo]
    return termo
```

**2.99** `[I]` Escreva uma variante do parser que gere nós **n-ários** para `+` e `*` (como em mlisp-v2) e *folding* binário à esquerda para `-` e `/`. Compare os interpretadores das duas versões: quais as vantagens e desvantagens de cada AST?

**2.100** `[I]` Implemente a associatividade à direita de `**` **sem recursão**: colete a sequência de operandos com um laço e faça o *folding* à direita. Em que condições essa abordagem é preferível?

**2.101** `[I]` Estenda o parser com os operadores `%` e `//` (exercício 2.78) e verifique, por testes, que a precedência e a associatividade esperadas são respeitadas.

**2.102** `[I]` Escreva um *gerador de testes* para o parser de `calc`: uma função que produz ASTs aleatórias, as converte para texto infixo com o mínimo de parênteses (exercício 2.12) e verifica que `parse(texto) == ast`. O que essa propriedade garante?

**2.103** `[C]` *Miniteste:* escreva, de memória, o pseudo-código de `parse_atomo`, `parse_fator`, `parse_termo` e `parse_exp` para a gramática EBNF final, indicando em cada ponto o *look-ahead* usado.

**2.104** `[C]` O parser descendente recursivo é apenas uma das estratégias de análise sintática. Cite outras famílias (por exemplo, *bottom-up*/LR e parsers com *backtracking*) e explique, em linhas gerais, o que elas fazem de diferente. Que tipo de gramática (recursão à esquerda, prefixos comuns) cada família tolera melhor, e por que o curso adota a abordagem LL(1)?

---
# Estágio 3 — Semântica de avaliação, variáveis e ambientes (Aulas 7 e 8)

### Ao final deste estágio você deve ser capaz de

- explicar a diferença entre semântica operacional de pequenos passos (*small-step*) e de passo grande (*big-step*), e ler e escrever julgamentos `⟨e, ρ⟩ ⇓ v`;
- identificar os domínios semânticos (`Val`, `Env`, operações semânticas) e explicar o papel de cada um;
- ler, aplicar e construir regras de inferência e derivações (em lista e em árvore indentada), reconhecendo a relação com a dedução natural vista em Lógica;
- explicar propriedades da semântica (determinismo, composicionalidade, relevância do ambiente) e reconhecer o que as quebraria;
- projetar operações semânticas totais (*lift*) e discutir como essa escolha simplifica as regras de erro;
- implementar um lexer tipado (`Token`, `TokenType`, regexes compostas) e justificar a ordem das categorias léxicas;
- explicar variáveis, ambientes, vinculação local (`let..in`), escopo léxico, sombreamento (*shadowing*), variáveis livres e a diferença entre avaliação por substituição e por ambiente;
- transcrever regras semânticas em uma função `eval(ast, env)` e implementar `calc` e `aljabr` completos, com testes.

---

## 3A — O lexer renovado (Aula 7)

**3.1** `[C]` O que significa programar em estilo *stringly-typed*? Por que as primeiras versões do curso usaram esse estilo e por que ele deixou de ser adequado? Que vantagens trazem um tipo `Token` (um `dataclass` *frozen*) e um tipo `TokenType` (um enumerado)?

**3.2** `[C]` Por que o `Token` é *frozen*? O que se ganha com imutabilidade (comparação, uso em conjuntos e dicionários, ausência de efeitos colaterais) e o que se perde?

**3.3** `[I]` Defina `TokenType` (como `Enum`) e `Token` (como `dataclass` imutável com tipo, texto e posição) para os tokens de `calc`: `INTEIRO`, `+`, `-`, `*`, `/`, `**`, `(`, `)` e espaço. Implemente uma função `tokenizar(texto) -> list[Token] | Erro`.

**3.4** `[C]` Explique a abordagem de formar **uma única regex** a partir de regexes independentes e simples, uma por tipo de token (por exemplo, com grupos nomeados em `TOKEN_SPEC`). Que vantagem tem em relação a testar cada regex separadamente em cada posição do texto?

**3.5** `[D]` Suponha `TOKEN_SPEC` com o `*` listado **antes** de `**`. Como `2 ** 3` é tokenizado? Por que isso ocorre, dado que a alternância `|` de regex em Python é *ordenada* (e não "a mais longa")? Corrija a especificação.

**3.6** `[P]` Considere os tokens `=`, `==`, `<`, `<=`, `->`, `-`, `**`, `*`, `INTEIRO`, `NOME`. Escreva uma ordem de listagem correta para o `TOKEN_SPEC`. Enuncie a regra geral que você usou.

**3.7** `[I]` Implemente a função `match_type(tipo)`, que devolve um **predicado** sobre tokens, e use-a para criar `LPAREN`, `RPAREN`, `INTEIRO` etc. Reescreva `peek` e `expect` do seu parser usando esses predicados.

**3.8** `[I]` Faça o lexer: (a) ignorar espaços; (b) registrar linha e coluna de cada token; (c) devolver um `Erro` indicando a posição do primeiro caractere desconhecido (por exemplo, em `2 $ 3`).

**3.9** `[C]` Por que erros léxicos são reportados antes da análise sintática? O que o seu lexer devolve ao encontrar um caractere desconhecido, e como isso se encaixa no tratamento monádico de erros?

---

## 3B — Semântica operacional big-step de `calc` (Aula 7)

**3.10** `[C]` Defina semântica operacional *small-step* e *big-step*. Em cada uma, como o significado de um programa é obtido? Por que a segunda também se chama *semântica natural* ou *semântica de avaliação*?

**3.11** `[C]` Leia em português o julgamento `⟨e, ρ⟩ ⇓ v`. O que são `e`, `ρ` e `v`? O que é "o significado" de um programa nesta notação?

**3.12** `[C]` Explique a notação de regras de inferência: o que ficam acima e abaixo da linha, o que é o nome da regra, o que é um axioma (regra sem premissas) e o que significa "se todas as premissas são deriváveis, a conclusão também é". Que paralelo pode ser feito com a dedução natural da disciplina de Lógica? O que faz o papel de "proposição" e de "prova"?

**3.13** `[C]` Defina *domínio semântico*. Para cada um dos itens `ℝ`, `Val = ℝ ∪ {erro}`, `Env = Var ⇀ Val` e `f_op`, diga o que representa e por que é necessário. Por que `Val` inclui `erro`? Por que o ambiente é uma função **parcial**? Por que ele é sempre vazio em `calc`?

**3.14** `[C]` Nas notas, o domínio é `ℝ`, mas a sintaxe abstrata fala em "divisão inteira". Discuta a inconsistência e defina precisamente `f_/` sobre os inteiros. Para operandos negativos, escolha entre truncamento e piso (compare Python e C) e justifique.

**3.15** `[P]` Leia a regra `Op` identificando suas três premissas. A ordem em que as premissas são escritas determina a ordem em que a avaliação ocorre? Em que ponto da implementação essa ordem é decidida?

**3.16** `[C]` Explique a regra `DivZero` e as regras `ErrEsq` e `ErrDir`. Compare-as com o esquema monádico de erros que usamos na implementação.

**3.17** `[P]` Construa a derivação (em lista numerada, como em aula) de cada programa usando as regras `Num`, `Op`, `DivZero`, `ErrEsq` e `ErrDir`. Indique, em cada linha, a regra usada e as linhas de que ela depende.

- `2 + 3 * 4`
- `(2 + 3) * 4`
- `10 / (5 - 5)`
- `(10 / (5 - 5)) + 1`
- `1 + (10 / (5 - 5))`
- `100 / 10 / 5`
- `8 - (3 - 1)`

**3.18** `[P]` Refaça duas das derivações acima como **árvore de derivação indentada** (conclusão na raiz, premissas como filhos) e compare com a AST da mesma expressão. Que relação existe entre as duas árvores?

**3.19** `[C]` "É a estrutura da AST, e não a ordem textual, que determina a ordem de avaliação." Ilustre com `2 + 3 * 4` e `(2 + 3) * 4`.

**3.20** `[C]` Existe algum programa para o qual **mais de uma regra** se aplica ao mesmo tempo (por exemplo, `(1 / 0) / 0`)? O resultado muda conforme a regra escolhida? Isso viola o determinismo da semântica?

**3.21** `[C]` Defina *estado bloqueado* (*stuck state*). Se a premissa "`f_op(v₁, v₂) = v`" não for satisfeita e **não** existir a regra `DivZero`, o que acontece ao derivar `⟨1 / 0, ρ⟩ ⇓ ?` Compare *travar* com *produzir o valor `erro`*.

**3.22** `[C]` Defina e discuta cada propriedade abaixo: *determinismo*, *composicionalidade* e *independência do ambiente*. Para cada uma, diga se vale para `calc`, justifique com base nas regras e invente uma regra hipotética que a quebraria.

**3.23** `[C]` O operador de entrada `?` de mlisp (exercício 2.29) preserva o determinismo e a composicionalidade da semântica `⟨e, ρ⟩ ⇓ v`? Que novo elemento teria de aparecer no julgamento para descrevê-lo com precisão?

**3.24** `[X]` Prove por indução estrutural em `e`, usando a versão com operações *lifted* (regra `Op` única), que: (a) se `⟨e, ρ⟩ ⇓ v₁` e `⟨e, ρ⟩ ⇓ v₂`, então `v₁ = v₂`; (b) em `calc`, se `⟨e, ρ₁⟩ ⇓ v`, então `⟨e, ρ₂⟩ ⇓ v` para todo `ρ₂`.

**3.25** `[C]` Compare dois conjuntos de regras: (i) `Op` com operações parciais, mais `DivZero`, `ErrEsq` e `ErrDir`; (ii) `Op` única com operações *lifted*. Quantas regras cada um tem? O que se ganha e o que se perde? O que significa dizer que "a escolha das regras e das operações semânticas é parte do projeto da linguagem"?

**3.26** `[I]` Implemente `eval(ast, env) -> Val` seguindo **literalmente** as regras: uma ramificação por regra e uma chamada recursiva por premissa. Monte uma tabela "regra → trecho de código" e escreva pelo menos um teste por regra.

**3.27** `[I]` Escreva `derivar(ast, env)`, que devolve o valor **e** a árvore de derivação (em texto indentado, com o nome da regra em cada linha). Compare a saída com as derivações que você fez à mão no exercício 3.17.

**3.28** `[C]` O interpretador em Python é *a especificação* da linguagem ou *uma implementação* dela? Que benefícios as regras formais trazem que o código não traz (clareza, independência de linguagem de implementação, possibilidade de provar propriedades)?

**3.29** `[C]` Faça uma tabela comparando as semânticas de transição de `rpn` (pequenos passos) e de `calc` (passo grande): forma do estado, número de regras, como o significado é obtido, como os erros se manifestam, qual é mais fácil de ler e qual é mais próxima do código.

**3.30** `[P]` Para o programa RPN `1 2 + 3 4 + *`, escreva a sequência de estados (pequenos passos) e, para a expressão infixa equivalente `(1 + 2) * (3 + 4)`, a árvore de derivação (passo grande). Compare o que cada uma mostra.

---

## 3C — `calc` revisitada: operações totais (*lift*) e operadores unários (Aula 8)

**3.31** `[C]` Explique o *lift*: dada uma função parcial `f : ℝ × ℝ ⇀ ℝ`, como se define `f↑ : Val × Val → Val`? Explique cada um dos três casos da definição (propagação de `erro`, valor original quando definido, `erro` quando indefinido). O que muda no domínio e no contradomínio?

**3.32** `[P]` Escreva `f↑` para `+`, `-`, `*`, `/` e `**` (sobre inteiros), listando explicitamente todos os casos em que a função original é indefinida. Decida e documente: expoente negativo, `0 ** negativo` e `0 ** 0`.

**3.33** `[C]` Com operações *lifted*, quais regras deixam de ser necessárias e por quê? Refaça a derivação de `10 / (5 - 5)` e de `(10 / (5 - 5)) + 1` com a regra única `Op` e compare o tamanho das derivações.

**3.34** `[C]` O *lift* é uma forma de propagar erros "em estilo monádico". Compare o *lift* das operações semânticas com o decorador `monadic_error` da Aula 2: o que cada um propaga, entre quais componentes e em qual nível da linguagem (implementação × semântica)?

**3.35** `[C]` Explique a seção "Exceções": se quisermos que `0 ** 0` valha `1`, uma regra específica `Pot00` é necessária. Mostre que, se `f**↑(0, 0)` for `erro`, as regras `Op` e `Pot00` se aplicam **simultaneamente** e com resultados diferentes, violando o determinismo. Proponha duas soluções (uma que altera a regra `Op`, outra que altera a operação semântica).

**3.36** `[P]` Escreva as regras de avaliação para os operadores **unários** `+` e `-` (com operações semânticas totais). Faça a derivação em árvore de:

- `- (3 + 4)`
- `-2 ** 2`
- `2 ** -1`
- `-2 * -3`

**3.37** `[C]` Representação de operadores unários na AST: compare `["-", x]` (com a aridade deduzida do tamanho da lista) com `["neg", x]`. Como o interpretador distingue `-` binário de `-` unário em cada caso? Compare com a questão análoga em RPN (exercício 1.12).

**3.38** `[P]` Com a EBNF efetiva de `calc-v4`:

```
exp     ::= termo { ( + | - ) termo }
termo   ::= fator { ( * | / ) fator }
fator   ::= unario [ ** fator ]
unario  ::= [ + | - ] atomo
atomo   ::= INTEIRO | ( exp )
```

diga se cada entrada é aceita, derivando-a ou justificando a rejeição: `-2 ** 2`, `2 ** -1`, `- - 2`, `-(-2)`, `+-2`, `-2 * -3`, `2 ** -(1 + 1)`. Desenhe a AST das aceitas.

**3.39** `[C]` Em `calc`, `-2 ** 2` é interpretada como `(-2) ** 2`; em Python, como `-(2 ** 2)`. Que posição na hierarquia de não-terminais explica cada comportamento? Reescreva a gramática para reproduzir o comportamento de Python (cuide para que `2 ** -1` continue válida) e compare as duas ASTs.

**3.40** `[P]` A gramática efetiva não permite repetição de operadores unários. Mostre as duas alternativas citadas: (a) `unario ::= ( + | - ) unario | atomo`; (b) `unario ::= { + | - } atomo`. Derive `- - 2` em (a), diga qual `peek` decide cada produção e explique como produzir a AST em (b) (*folding*).

**3.41** `[C]` Resuma, em uma tabela, a precedência e a associatividade de **todos** os operadores de `calc-v4` (inclusive os unários) e o não-terminal que implementa cada nível. Por que `**` é implementado por recursão à direita (`[ ** fator ]`) enquanto `+` e `*` usam laços?

**3.42** `[C]` Por que "precisamos fazer nossa gramática LL(1), e portanto sem recursão à esquerda, e ainda assim a linguagem exige as associatividades indicadas"? Como ambas as exigências são satisfeitas ao mesmo tempo?

**3.43** `[I]` Implemente `calc-v4` completa: lexer tipado, parser LL(1) com operadores unários, interpretador com operações *lifted*, e tratamento de todos os níveis de erro. Escreva testes para erros léxicos, sintáticos e semânticos.

**3.44** `[D]` Monte uma tabela com 15 expressões aritméticas e compare o resultado de `calc-v4` com o de Python. Documente cada divergência e explique-a como uma decisão de design (por exemplo, `-2 ** 2`, divisão inteira, `0 ** 0`, expoente negativo, divisão por zero).

---

## 3D — `aljabr`: variáveis, `let..in` e ambientes (Aula 8)

### Variáveis e sintaxe

**3.45** `[C]` O que é uma variável? Cite formas diferentes de introduzir variáveis em linguagens de programação. Por que o curso começa por `let..in`? O que `aljabr` **ainda não** tem (estado, mutabilidade)?

**3.46** `[C]` Descreva a sintaxe abstrata `let <var> = <exp1> in <exp2>`: o que é avaliado, em que ordem, e qual o escopo da variável. Por que dizemos que é uma variável "local, com escopo delimitado à própria expressão"?

**3.47** `[P]` Avalie à mão cada programa, dizendo qual valor `x` (e `y`, `z`) assume em cada ponto:

- `let x = 10 in (x - 1) * (x + 1)`
- `let x = 3 * 3 + 1 in (x - 1) * (x + 1)`
- `let x = 10 in let y = x + 1 in let z = x - 1 in x + y * z`
- `let x = 1 in let y = x + 1 in let x = y * 10 in x + y`
- `let x = 5 in let y = (let x = 2 in x * x) in x + y`

**3.48** `[P]` Com a EBNF de `aljabr`:

```
exp    ::= let NOME = exp in exp
         | termo { ( + | - ) termo }
termo  ::= fator { ( * | / ) fator }
fator  ::= unario [ ** fator ]
unario ::= [ + | - ] atomo
atomo  ::= INTEIRO | NOME | ( exp )
```

derive `let x = 2 in x + 1`, desenhe a árvore de derivação e a AST (defina você mesmo a representação do nó `let`).

**3.49** `[P]` Decida se cada programa é sintaticamente válido e, quando for, desenhe a AST e calcule o valor. Justifique pelas regras da gramática.

- `let x = 1 in x + 2`
- `(let x = 1 in x) + 2`
- `1 + let x = 2 in x`
- `1 + (let x = 2 in x)`
- `let x = 1 in x * let y = 2 in y`
- `let x = 1 in x * (let y = 2 in y)`

**3.50** `[C]` O `let` foi colocado no mesmo nível de `exp`, com menor precedência que `+` e `-`. O que isso implica sobre até onde se estende o corpo do `let`? Como `let x = 1 in x + 2` é agrupado? Por que `atomo` não inclui `let` sem parênteses?

**3.51** `[C]` Aninhamento: por que as produções de `exp` permitem o uso de múltiplas variáveis "sem nenhum problema"? Por que o uso de parênteses para o aninhamento é opcional?

**3.52** `[C]` Palavras reservadas: o que são e por que `let` e `in` não podem ser nomes de variáveis? Mostre a ambiguidade de `let in = 3 in in`. Em que parte do pipeline elas são tratadas?

**3.53** `[D]` Se `NOME` estiver **antes** de `let` e `in` no `TOKEN_SPEC`, o que acontece? Proponha duas formas de resolver (reordenar o `TOKEN_SPEC` ou verificar o texto do `NOME` depois de reconhecido) e compare-as. Cuide do caso `letter`, que **não** pode ser reconhecido como `let` seguido de `ter`.

### Semântica

**3.54** `[C]` Que domínios semânticos mudam de `calc` para `aljabr`? Por que nenhum domínio novo é necessário? Qual o papel de `Var`?

**3.55** `[P]` Calcule, para `ρ = {x ↦ 1, y ↦ 2}`: `ρ[x ↦ 5](x)`, `ρ[x ↦ 5](y)`, `ρ[z ↦ 0](z)` e `ρ[x ↦ 1][x ↦ 2](x)`. Escreva o domínio de cada um desses ambientes.

**3.56** `[C]` Por que `ρ[x ↦ v]` é definido como uma **nova** função em vez de modificar `ρ`? Que diferença isso faz para o ambiente *externo* depois que o `let` termina?

**3.57** `[C]` Defina o ambiente *lifted* `ρ↑`, que devolve `erro` para variáveis inexistentes. Como a regra `Var` fica nesse caso? Que regra deixa de ser necessária?

**3.58** `[P]` Leia em português as regras `Var`, `VarNaoLigada` e `Let`, enumerando as premissas de cada uma. Em qual ambiente `e₁` é avaliada e em qual `e₂`?

**3.59** `[C]` Por que `x` **não** está em escopo dentro de `e₁`? Diga o que acontece nos programas `let x = x + 1 in x` (com `ρ = ∅`) e `let x = 1 in let x = x + 1 in x`. O que isso diz sobre a ordem de avaliação e sobre recursão?

**3.60** `[P]` Construa a derivação em **árvore indentada** (com nome da regra, "operação semântica" e "acesso ao ambiente") de cada programa, com `ρ = ∅`:

- `let x = 2 + 3 in x * x`
- `let x = 1 in (let x = 2 in x) + x`
- `let x = 1 in x + y`
- `let a = 2 in let b = a * a in b + a`
- `let x = 5 in let y = (let x = 2 in x * x) in x + y`
- `let x = 1 in let x = x + 1 in x`

**3.61** `[C]` Defina *sombreamento* (*shadowing*). Em `let x = 1 in (let x = 2 in x) + x`, a que `x` refere-se cada ocorrência? Como `ρ[x ↦ v]` implementa isso? Por que sombreamento **não** é atribuição?

**3.62** `[C]` Defina *escopo léxico* (ou *estático*) e *escopo dinâmico*. Em `aljabr`, uma ocorrência de variável é resolvida pelo `let` sintaticamente mais próximo que a vincula. Por que não existe programa de `aljabr` cujo resultado difira entre os dois critérios? Que construção teria de ser acrescentada à linguagem para que eles divergissem?

**3.63** `[C]` Explique as duas estratégias de avaliação de variáveis: *substituição textual* e *ambiente*. Avalie `let x = 3 in x + x` pelas duas. Mostre que a substituição ingênua falha em `let x = 1 in (let x = 2 in x) + x` (o que acontece se substituirmos todos os `x` do corpo por `1`?) e descreva como corrigi-la.

**3.64** `[P]` Defina *ocorrência livre* de uma variável. Calcule as variáveis livres de:

- `x + y`
- `let x = 1 in x + y`
- `let x = y in x`
- `let x = 1 in let y = x in z`
- `(let x = 1 in x) + x`

Em seguida, escreva a definição recursiva de `fv(e)` para cada forma de expressão (número, variável, operação, `let`). Qual o cuidado necessário no caso do `let`?

**3.65** `[C]` O que é um programa *fechado*? Que relação existe entre ser fechado e nunca usar a regra `VarNaoLigada` quando `ρ = ∅`?

**3.66** `[C]` Pureza: liste o que `aljabr` **não** tem (atribuição, sequenciamento, laços, condicionais). Explique como o `let` altera o ambiente sem mutação e por que isso preserva composicionalidade e determinismo. Que propriedade seria mais difícil de garantir se acrescentássemos `x := e`?

**3.67** `[C]` Revise as propriedades da semântica de `aljabr` (determinismo, composicionalidade, ambiente relevante, ausência de recursão). Justifique cada uma e diga em que ponto `aljabr` difere de `calc`.

**3.68** `[X]` Prove por indução estrutural em `e` que: (a) se `x ∉ fv(e)`, então `⟨e, ρ[x ↦ v]⟩ ⇓ w` se e somente se `⟨e, ρ⟩ ⇓ w`; (b) se `fv(e) ⊆ dom(ρ)`, a derivação de `⟨e, ρ⟩ ⇓ v` nunca usa a regra `VarNaoLigada`.

**3.69** `[C]` Compare a notação de Gentzen (premissas acima da linha) com a árvore indentada usada em aula: que vantagens e desvantagens cada uma tem para escrever e ler derivações? Converta a regra `Let` para o formato de árvore indentada.

**3.70** `[X]` Escreva as regras semânticas para um `let` com **dois** vínculos, `let x = e₁, y = e₂ in e₃`, em duas versões: (a) *sequencial* (`e₂` enxerga `x`); (b) *paralela* (`e₂` **não** enxerga `x`). Dê um programa em que o resultado difira. Como cada versão pode ser reescrita com `let` aninhados?

### Implementação

**3.71** `[I]` Implemente `aljabr`: lexer tipado com `LET`, `IN`, `NOME` e `=`; parser a partir da EBNF; `eval(ast, env)` com ambiente como `dict` copiado (`{**env, x: v}`). Teste todos os programas dos exercícios 3.47, 3.49, 3.59 e 3.60 e também erros: variável não vinculada, `in` faltando, palavra reservada como nome, `let = 3 in 4`, `let x 3 in x`.

**3.72** `[I]` Reimplemente o ambiente como uma **lista de dicionários** (cadeia de escopos), com busca do mais interno para o mais externo. Verifique, com a mesma bateria de testes, que o comportamento é idêntico. Compare custo de cópia, memória e a forma de representar o sombreamento.

**3.73** `[I]` Implemente `substituir(e, x, v)`, respeitando o sombreamento, e um avaliador por substituição. Verifique com testes aleatórios que, para programas fechados, os dois avaliadores (substituição e ambiente) produzem o mesmo resultado.

**3.74** `[I]` Implemente `fv(e)` e uma *verificação prévia* que reporta variáveis não vinculadas **antes** de qualquer avaliação. Em que momento do pipeline esse erro é detectado agora? Que diferença existe entre detectá-lo antes ou durante a avaliação (por exemplo, em `1 / 0 + y`)?

**3.75** `[I]` Estenda `derivar` (exercício 3.27) para `aljabr`, imprimindo as árvores no formato usado em aula, com os nós "acesso ao ambiente" e "operação semântica". Compare com as suas derivações do exercício 3.60.

**3.76** `[I]` Escreva `aljabr` de modo que a tabela "regra → código" seja evidente: uma função por regra, nomeada como a regra (`regra_num`, `regra_var`, `regra_op`, `regra_let`), com um *dispatcher*. Explique, em um comentário, por que o código é uma "leitura quase literal" das regras.

---

# Questões integradoras (Estágios 1 a 3)

**I.1** `[C]` Acompanhe o programa `let x = 2 in x * (3 + x)` por todo o pipeline: texto, tokens, AST, derivação e valor. Mostre cada representação intermediária e dê uma variação do programa para cada tipo de erro (léxico, sintático, semântico).

**I.2** `[C]` Monte uma tabela com `rpn`, `mlisp`, `calc` e `aljabr` comparando: estilo da sintaxe concreta, necessidade de parser, presença de precedência e associatividade, estado da computação na semântica (pilha, ambiente), formalismo semântico usado e abordagem de erros.

**I.3** `[C]` Liste ao menos oito **decisões de design** tomadas ao longo do curso (notação, parênteses, associatividade de `**`, precedência de `let`, precedência do menos unário, operações parciais × totais, erro como valor, `let` não recursivo, palavras reservadas, escopo léxico etc.). Para cada uma, indique pelo menos uma alternativa e o que ela implicaria.

**I.4** `[C]` Para cada estágio, indique qual metalinguagem especifica o léxico, a sintaxe e a semântica (linguagem natural, Python, expressões regulares, BNF, EBNF, regras de transição, regras de passo grande). Por que usar mais de uma?

**I.5** `[C]` "Sintaxe e semântica são dimensões independentes de uma linguagem." Apresente evidências do Estágio 2 e dê um exemplo em que uma mudança de sintaxe exige mudança de semântica (por exemplo, o menos unário ou o `let`).

**I.6** `[C]` Explique como o modelo de computação de cada linguagem (pilha em `rpn`, recursão sobre a AST em `calc`, recursão com ambiente em `aljabr`) molda as decisões de implementação do interpretador.

**I.7** `[I]` Construa uma ferramenta de linha de comando `plp rpn|lisp|infix|aljabr "<programa>"` que imprima os tokens, a AST e o resultado, com uma opção `--derivacao` que mostre a árvore de derivação (quando aplicável). Todas as três notações aritméticas devem compartilhar o **mesmo** interpretador.

**I.8** `[I]` Escreva um tradutor entre as notações (infixa ↔ s-expressão ↔ RPN) usando os parsers e os impressores de AST. Escreva um teste de *ida e volta*: `parse(imprimir(ast)) == ast` para ASTs aleatórias.

**I.9** `[I]` Proponha e implemente uma estratégia de testes para um interpretador: testes unitários por camada (lexer, parser, interpretador), testes de erro para cada nível e testes baseados em propriedades (por exemplo, equivalência entre o avaliador por ambiente e o por substituição). Mostre a cobertura obtida.

**I.10** `[C]` *(Pesquisa.)* Para cada conceito — RPN, s-expressões, precedência infixa, menos unário, `let..in`, sombreamento, palavras reservadas — cite uma linguagem real que fez a mesma escolha que o curso e outra que fez uma escolha diferente. Explique a diferença.

**I.11** `[X]` *Mini-projeto:* escolha uma extensão de `aljabr` (por exemplo, módulo `%`, números decimais, comentários, funções primitivas como `min` e `max`) e percorra o ciclo completo do curso: (1) problema; (2) decisão de design; (3) sintaxe (léxico e EBNF); (4) semântica informal; (5) implementação; (6) formalização (regras); (7) alternativas; (8) linguagens reais que fizeram escolhas semelhantes ou diferentes.

---

# Checklist de competências

Marque cada item quando conseguir fazê-lo **sem consultar as notas**.

### Estágio 1

- [ ] Converter expressões entre as notações infixa, prefixa e posfixa e avaliá-las
- [ ] Construir a tabela de rastreamento de um programa RPN
- [ ] Implementar um interpretador RPN com pilha
- [ ] Explicar lexer, parser e interpretador, e o tipo de erro de cada etapa
- [ ] Tratar erros de forma monádica e explicar por que erros são "significados"
- [ ] Distinguir linguagem-objeto e metalinguagem
- [ ] Escrever expressões regulares para o léxico e BNF para a sintaxe
- [ ] Derivar programas a partir de uma gramática
- [ ] Escrever regras de transição e identificar sucesso e erro

### Estágio 2

- [ ] Distinguir sintaxe concreta e abstrata e desenhar ASTs
- [ ] Relacionar percursos em árvore com as notações prefixa, infixa e posfixa
- [ ] Explicar por que uma s-expressão é uma AST textual
- [ ] Implementar o pareamento de parênteses (contador e pilha) e um parser de s-expressões
- [ ] Derivar mecanicamente um parser descendente recursivo (`peek`, `expect`)
- [ ] Explicar LL(1) e decidir se uma gramática é LL(1)
- [ ] Ler e escrever EBNF e convertê-la em código
- [ ] Explicar aridade, associatividade e precedência e codificá-las na gramática
- [ ] Reconhecer e eliminar ambiguidade
- [ ] Eliminar produções vazias e recursão à esquerda, e fatorar à esquerda
- [ ] Explicar o *folding* e implementar o parser LL(1) de `calc`

### Estágio 3

- [ ] Diferenciar semântica *small-step* e *big-step*
- [ ] Ler e escrever julgamentos `⟨e, ρ⟩ ⇓ v` e regras de inferência
- [ ] Construir derivações em lista e em árvore indentada
- [ ] Explicar determinismo, composicionalidade e relevância do ambiente
- [ ] Projetar operações totais (*lift*) e simplificar regras de erro
- [ ] Implementar um lexer tipado com regexes compostas e justificar a ordem das categorias
- [ ] Explicar ambiente, vinculação, escopo léxico e sombreamento
- [ ] Calcular variáveis livres
- [ ] Comparar avaliação por substituição e por ambiente
- [ ] Transcrever regras em `eval(ast, env)` e implementar `calc` e `aljabr`

---
