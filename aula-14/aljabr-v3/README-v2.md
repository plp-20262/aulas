# Especificação de `aljabr`

A principal mudança na especificação da LP `aljabr` versão `v2` em comparação à
versão `v1` é a inclusão de lambdas e closures.

## 1. Léxico

A linguagem `aljabr` versão `v2` inclui três novas categorias léxicas: `FN`,
`ARROW` e `COMMA`, as três necessárias para dar suporte a expressões e
aplicações de funções lambda. O conjunto de categorias léxias completo de
`aljabr` v2 fica assim:

```text
POW      ::=  \*\*
ADD      ::=  \+
SUB      ::=  -
MULT     ::=  \*
DIV      ::=  /
LPAREN   ::=  \(
RPAREN   ::=  \)
ARROW    ::=  =>                     ← NOVO
EQUAL    ::=  =
COMMA    ::=  ,                      ← NOVO
INTEIRO  ::=  [0-9]+
NOME     ::=  [a-z_][a-z0-9_]*       (exceto as palavras reservadas)
```

**Palavras reservadas** Há apenas três na linguagem: `let`, `in` e `fn`. 

A ordem das regras importa e é a indicada acima, para garantir que o lexer não
confunda `=>` com um `=` seguido por um `>` ou o `**` com dois `*`.

## 2. Sintaxe

Esta é a EBNF efetiva a usar para derivar o parser.

```python
exp     ::= let NOME = exp in exp
          | fn LPAREN [ params ] RPAREN => exp                      ← NOVO
          | termo { ( + | - ) termo }
termo   ::= fator { ( * | / ) fator }
fator   ::= unario [ ** fator ]
unario  ::= [ + | - ] chamada                                       ← ALTERADO
chamada ::= atomo { LPAREN [ args ] RPAREN }                        ← NOVO
atomo   ::= INTEIRO | NOME | LPAREN exp RPAREN
params  ::= NOME { , NOME }                                         ← NOVO
args    ::= exp { , exp }                                           ← NOVO
```

## 3. Semântica 

A semântica é expressa no estilo semântica operacional big-step (ou semântica
natural), baseada em regras de derivação. Abaixo definimos os domínios
semânticos necessários. Observe que apenas precisamos incluir o conjunto
$\mathrm{Clo}$, o conjunto de closures.

| Domínio                                                                          | Descrição                                            |
|----------------------------------------------------------------------------------|------------------------------------------------------|
| $ℝ$                                                                              | Os números reais.                                    |
| $\mathrm{Clo} = \mathrm{Var}^* \times \mathrm{Exp} \times \mathrm{Env}$          | _Closures_: (parâmetros, corpo, ambiente de criação) |
| $\mathrm{Val} = ℝ ∪ \mathrm{Clo} ∪ \\{ \mathtt{erro} \\}$                        | Valores possíveis                                    |
| $\mathrm{Env} = \mathrm{Var} ⇀ \mathrm{Val}$                                     | Ambientes                                            |

Um closure é essencialmente uma tripla. Contudo usaremos uma notação mais
legível e bastante usada para expressar domínios semânticos: closures serão
expressos como $\mathsf{clo}((p_1, \ldots, p_n),\, e,\, \rho)$. A parte
$\mathsf{clo}$ é apenas para melhorar a legibilidade.

**Notação.** Para vincular vários parâmetros de uma vez, usaremos a extensão
sucessiva do ambiente:

$$
\rho[p_1 \mapsto v_1, \ldots, p_n \mapsto v_n]
= (\cdots(\rho[p_1 \mapsto v_1])[p_2 \mapsto v_2] \cdots)[p_n \mapsto v_n]
$$

### Operações Semânticas e Operadores

Mais uma vez, para simplificar as regras de inferência, usarei apenas operações
semânticas totais, obtidas através de um _lift_. Ou seja, as operações
retornarão $\mathrm{erro}$ para todo valor do domínio em que a original esteja
indefinida. As funções lifted também devem propagar erros em estilo monádico.
Esta decisão permite eliminar as regras de inferência para lidar com erros de
funções parciais e as regras de propação de erro.

**Notação** Nos referiremos às operações semânticas com a notação
$f_{\text{op}}$ (original) e $f_{\text{op}}^{\uparrow}$ (_lifted_), para à
operação relacionada ao operador $\text{op}$. Por exemplo, para a operação de
soma podemos usar $f_{+}$ (original) e $f_{+}^{\uparrow}$ (_lifted_).

Se assumirmos que cada operação semântica original é uma função parcial

$$
f_{\mathrm{op}} : \mathbb{R} \times \mathbb{R} \rightharpoonup \mathbb{R},
$$

podemos definir sua versão _lifted_ como uma função total

$$
f_{\mathrm{op}}^{\uparrow} :
\mathrm{Val} \times \mathrm{Val}
\to
\mathrm{Val},
$$

em que $\mathrm{Val} = \mathbb{R} \cup \\{ \mathbf{erro} \\}$. A função _lifted_
propaga $\mathbf{erro}$ e transforma em $\mathbf{erro}$ qualquer aplicação da
operação original para a qual ela não esteja definida:

$$
f_{\mathrm{op}}^{\uparrow}(v_1,v_2) =
\begin{cases}
\mathbf{erro},
  & \text{se } v_1 = \mathbf{erro}\ \text{ou}\ v_2 = \mathbf{erro}, \\
f_{\mathrm{op}}(v_1,v_2),
  & \text{se } v_1,v_2 \in ℝ\ \text{e} \ f_{\mathrm{op}}(v_1,v_2)\mathrel{\downarrow}, \\
\mathbf{erro},
  & \text{caso contrário}.
\end{cases}
$$

Aqui, $f_{\mathrm{op}}(v_1,v_2)\mathrel{\downarrow}$ significa que a função
parcial $f_{\mathrm{op}}$ está definida para o par $(v_1,v_2)$ (notação
convencional de lógica matemática, computabilidade e funções parciais).


### Regras de Avaliação

#### Regras herdadas de aljbr versão v1

As regras abaixo são transcritas da especificação da versão v1 de `aljabr`.
Ressalvo que usamos usamos o ambiente _lifted_, o que nos permite dispensar a
regra (VarNaoLigada) vista e apresentada na especificação anterior, apenas como
alternativa, caso não usássemos _lift_. 

$$
\frac{}{\langle n, \rho \rangle \Downarrow n} \quad \text{(Num)}
\qquad
\frac{\rho(x) = v}{\langle x, \rho \rangle \Downarrow v} \quad \text{(Var)}
$$

$$
\frac{
  \langle e_1, \rho \rangle \Downarrow v_1 \qquad
  \langle e_2, \rho[x \mapsto v_1] \rangle \Downarrow v_2
}{
  \langle \text{let } x = e_1 \text{ in } e_2, \rho \rangle \Downarrow v_2
} \quad \text{(Let)}
$$

$$
\frac{
  \langle e_1, \rho \rangle \Downarrow v_1 \qquad
  \langle e_2, \rho \rangle \Downarrow v_2
}{
  \langle e_1 \text{ op } e_2, \rho \rangle \Downarrow f_{\mathrm{op}}^{\uparrow}(v_1, v_2)
} \quad \text{(Op)}
$$

(As regras dos operadores unários são análogas.) Lembre que $f^{\uparrow}$ é o
_lift_ da operação parcial $f$:

$$
f^{\uparrow}(v_1, v_2) =
\begin{cases}
f(v_1, v_2) & \text{se } v_1, v_2 \in ℝ \text{ e } (v_1, v_2) \in \mathrm{dom}(f) \\
\mathtt{erro} & \text{caso contrário}
\end{cases}
$$

> **Observe:** como $\mathrm{Val}$ agora inclui closures, o "caso contrário"
> do _lift_ cobre também as operações aritméticas aplicadas a funções. Não
> precisaremos de nenhuma regra nova para `q + 1` quando `q` for uma função: o
> _lift_ que já tínhamos produz `erro`.

**Ambiente _lifted_.** Como na especificação anterior, usamos uma versão
_lifted_ de `ρ`: para toda variável `x ∉ dom(ρ)`, definimos `ρ(x) = erro`.
Assim, a regra ($\mathrm{Var}$) cobre também as variáveis não vinculadas, e não
precisamos de uma regra à parte para isso.

**Convenção de propagação de erro.** As regras desta unidade descrevem apenas
o caso em que as premissas produzem valores "de verdade" (elementos de
$ℝ ∪ \mathrm{Clo}$). Para os demais casos, adotamos uma convenção, declarada
uma única vez, válida para todas as regras:

> se alguma premissa da forma $⟨e, ρ⟩ ⇓ v$ produz $v = \mathbf{erro}$, a regra
> não se aplica e a conclusão é $\mathbf{erro}$.

Esta convenção abrevia as regras de propagação que teríamos que escrever uma a
uma, para cada construção da linguagem. Trata-se do equivalente formal ao
tratamento monádico de erros da implementação: o erro interrompe a avaliação
assim que aparece (erros são **estritos**). Em particular, `let x = 1/0 in 5`
vale `erro`, e não `5`.

#### Regras novas para definição e aplicação de funções

**Criação de closure.** Um lambda avalia para um closure que captura e
"congela" o ambiente corrente:

$$
\frac{}{
  \langle \texttt{fn}\ (p_1, \ldots, p_n) \Rightarrow e,\ \rho \rangle
  \Downarrow
  \mathsf{clo}((p_1, \ldots, p_n),\ e,\ \rho)
} \quad \text{(Lam)}
$$

**Aplicação.**

$$
\frac{
  \begin{matrix}
  \langle e_f, \rho \rangle \Downarrow \mathsf{clo}((p_1, \ldots, p_n), e_b, \rho_0) \\
  \rule{0pt}{6ex}
  \langle a_i, \rho \rangle \Downarrow v_i \quad (1 \le i \le n) \\
  \rule{0pt}{6ex}
  \langle e_b, \rho_0[p_1 \mapsto v_1, \ldots, p_n \mapsto v_n] \rangle \Downarrow v \\
  \rule{0pt}{3ex}
  \end{matrix}
}{
  \langle e_f(a_1, \ldots, a_n), \rho \rangle \Downarrow v
} \quad \text{(App)}
$$

#### Regras de erro da aplicação

Há duas maneiras de uma aplicação **originar** um erro, uma por regra. Os erros
que apenas se _propagam_ (um argumento que avalia para `erro`, ou um corpo que
resulta em `erro`) não precisam de regra própria: são cobertos pela convenção
de erros já mencionada e pela própria regra (App), cujo valor é o valor do
corpo.

**Aplicar algo que não é função:**

$$
\frac{
  \langle e_f, \rho \rangle \Downarrow v_f \qquad v_f \notin \mathrm{Clo}
}{
  \langle e_f(a_1, \ldots, a_m),\ \rho \rangle \Downarrow \mathbf{erro}
} \quad \text{(AppNaoFuncao)}
$$

**Número errado de argumentos:**

$$
\frac{
  \langle e_f, \rho \rangle \Downarrow \mathsf{clo}((p_1, \ldots, p_n),\ e_b,\ \rho_0)
  \qquad m \neq n
}{
  \langle e_f(a_1, \ldots, a_m),\ \rho \rangle \Downarrow \mathbf{erro}
} \quad \text{(AppAridade)}
$$

Observe duas escolhas de projeto:

- a **aridade é verificada antes** de avaliar os argumentos (passo 2 antes do
  passo 3 da Aula 09);
- `erro` não pode ser passado como argumento: um argumento que avalia para
  `erro` interrompe a aplicação, pela convenção de propagação da Seção 4.2. Assim,
  as três regras de aplicação, (App), (AppNaoFuncao) e (AppAridade), são
  mutuamente exclusivas.


## 4. Como derivar a implementação da especificação

> Nesta seção, apenas o mapa. A implementação de referência será apresentada
> no início da Aula 12. Use este mapa para implementar você mesmo.

### 4.1 Léxico → lexer

| Especificação                          | Implementação                                             |
|----------------------------------------|-----------------------------------------------------------|
| três novas categorias léxicas          | três novos tipos de token e três novas entradas na lista de regras |
| `=>` antes de `=`                      | posição de `ARROW` na lista, antes de `EQUAL`             |
| `fn` é palavra reservada               | nova entrada no mapa de palavras reservadas               |

### 4.2 EBNF → parser

Relembre a correspondência entre EBNF e funções do parser (Aulas 04 e 05):

| Na EBNF         | Parser descendente recursivo                                  |
|-----------------|---------------------------------------------------------------|
| `{ X }`         | `while` o próximo token pode iniciar `X`                      |
| `[ X ]`         | `if` o próximo token pode iniciar `X`                         |
| terminal `T`    | `expect(T)`                                                   |
| não-terminal    | chamada à função correspondente                               |

E o que muda nas regras da gramática:

| Regra                       | Função do parser                                         |
|-----------------------------|----------------------------------------------------------|
| `exp` (alternativa `fn`)    | em `parse_exp`: se o próximo token é `FN`, chama `parse_lambda` |
| `params`                    | nova: `parse_params`                                     |
| `args`                      | nova: `parse_args`                                       |
| `chamada`                   | nova: `parse_chamada`                                    |
| `unario`                    | passa a chamar `parse_chamada` em vez de `parse_atomo`   |

Como exemplo da derivação mecânica, eis o pseudo-código de `parse_chamada`:

```python
def parse_chamada(stream):
    """chamada ::= atomo { LPAREN [ args ] RPAREN }"""
    ast = parse_atomo(stream)
    while peek(LPAREN):               # { … } vira while
        expect(LPAREN)
        args = []
        if not peek(RPAREN):          # [ … ] vira if
            args = parse_args(stream)
        expect(RPAREN)
        ast = App(ast, args)          # agrupamento à esquerda: f(1)(2) = (f(1))(2)
    return ast
```

As funções `parse_lambda`, `parse_params` e `parse_args` seguem o mesmo método
(ficam como exercício). A gramática continua sendo LL(1): `FN` decide a
alternativa de `exp`; `NOME` ou `RPAREN` decidem se há `params` ou `args`; e
um `LPAREN` logo após um `atomo` só pode iniciar uma aplicação.

> **Questão de projeto (pense antes de implementar):** a AST que construímos
> até aqui é feita de listas, e o `eval` decide qual regra aplicar olhando a
> forma da lista (seu primeiro elemento e seu tamanho). `Lambda` e `App`
> também podem ter 2 ou 3 componentes. Como evitar que sejam confundidos com
> operadores unários e binários?

### 4.3 Regras de avaliação → eval

A assinatura de `eval` não muda: `eval(ast, env) -> Val`. Cada regra vira uma
cláusula. Para a regra (App), leia as premissas como instruções:

| Parte da regra                                            | O que o `eval` faz                                              |
|-----------------------------------------------------------|-----------------------------------------------------------------|
| $\langle e_f, \rho \rangle \Downarrow \mathsf{clo}(\ldots)$ | avalia `e_f` em `env` e verifica que o resultado é um closure   |
| $m \neq n$                                                | compara o número de argumentos com o de parâmetros              |
| $\langle a_i, \rho \rangle \Downarrow v_i$                | avalia cada argumento em `env`, o ambiente **de chamada**       |
| $\rho_0[p_1 \mapsto v_1, \ldots]$                         | cria um novo dicionário a partir do ambiente **do closure**     |
| $\langle e_b, \ldots \rangle \Downarrow v$                | avalia o corpo no novo ambiente e devolve o resultado           |

E para a regra (Lam): empacotar `(params, corpo, env)` em um closure, sem
avaliar o corpo. Um closure é uma tripla; em Python, uma tupla ou uma
`dataclass` imutável com três campos serve bem.

Observe que as regras `AppNaoFuncao` e `AppAridade` correspondem aos dois
pontos em que o `eval` _origina_ um `Erro` na aplicação. Já a propagação de
erro (um argumento, ou o corpo, que resulta em `Erro`) é a convenção da §4.2: o
`eval` apenas devolve o erro recebido, sem prosseguir. E lembre que o _lift_
das operações já trata o caso de funções em expressões aritméticas.

### 4.4 Conjunto de testes

Use os programas abaixo para testar sua implementação.

| Programa                                                           | Resultado |
|--------------------------------------------------------------------|-----------|
| `let quad = fn (x) => x * x in quad(3) + quad(5)`                  | `34`      |
| `(fn (x, y) => x + y)(2, 3)`                                       | `5`       |
| `(fn () => 42)()`                                                  | `42`      |
| `(fn (x) => fn (y) => x + y)(2)(3)`                                | `5`       |
| `let n = 7 in let soma_n = fn (x) => x + n in let n = 100 in soma_n(3)` | `10` |
| `let f = fn (x) => x in -f(2)`                                     | `-2`      |
| `let f = fn (x) => x in f(2) ** 2`                                 | `4`       |
| `let f = fn (x, y) => x + y in f(1)`                               | `erro`    |
| `5(3)`                                                             | `erro`    |
| `let q = fn (x) => x in q + 1`                                     | `erro`    |
| `let f = fn (x) => x + y in 10`                                    | `10`      |
| `let f = fn (x) => x + y in f(1)`                                  | `erro`    |
| `let x = 1/0 in 5`                                                 | `erro`    |
| `(fn (x) => 5)(1/0)`                                               | `erro`    |

E os programas abaixo devem ser **rejeitados pelo parser**:
`fn x => x`, `fn (x,) => x`, `f(1,)`, `fn (x) x`, `1 + fn (x) => x`,
`let fn = 1 in fn`.


## Bloco 7: Prévia de escopo dinâmico e fechamento

### 7.1 Uma diferença de um único símbolo

Na regra (App), o corpo é avaliado em $\rho_0[\ldots]$, o ambiente de criação.
Imagine uma outra regra, idêntica em tudo, exceto por uma letra:

```math
\frac{
  \begin{array}{c}
  \langle e_f, \rho \rangle \Downarrow \mathsf{xclo}((p_1, \ldots, p_n),\ e_b,\ \rho_0) \\
  \rule{0pt}{6ex} \langle a_i, \rho \rangle \Downarrow v_i
  \quad (1 \le i \le n) \\
  \rule{0pt}{6ex} \langle e_b,\ \rho[p_1 \mapsto v_1, \ldots, p_n \mapsto v_n] \rangle \Downarrow v
  \end{array}
}{
  \langle e_f(a_1, \ldots, a_n),\ \rho \rangle \Downarrow v
} \quad \text{(AppDin)}
```

> **Pergunta à turma:** o que mudou? O que passa a acontecer com o programa
> abaixo?
>
> ```text
> let a = 10 in
> let f = fn (x) => x + a in
> let a = 20 in
> f(5)          # (App): 15      (AppDin): 25
> ```
>
> Observe que, com (AppDin), o ambiente `ρ₀` guardado no closure nunca é
> usado. Seria ele ainda necessário?

Essa é a diferença entre escopo **léxico** e escopo **dinâmico**, tema central
da Aula 12. Por ora, registre: `aljabr` usa escopo léxico, e a Aula 12 mostra
o que se perde e o que se ganha com a outra escolha.

### 7.2 Resumo

Nestas duas últimas aula:

1. especificamos `aljabr` v2 nos três níveis: REGEX (3 novos tokens), EBNF
   (lambda, aplicação, parâmetros e argumentos) e regras de avaliação (closure
   e aplicação);
2. vimos que a regra (App) concentra a decisão de design mais importante da
   unidade: o corpo é avaliado no ambiente **de criação**, estendido com os
   argumentos;
3. vimos como cada especificação se traduz em uma parte da implementação.


