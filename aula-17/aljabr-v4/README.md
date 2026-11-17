# Especificação de `aljabr`

A principal mudança na especificação da LP `aljabr` versão `v3` em comparação à
versão `v2` é a inclusão do `se`, uma forma especial de expressão, e do
`let-rec` outra forma especial de expressão que permite a definição recursiva
de funções (lambdas que são imediatamente associados a um nome e cujo nome pode
ser usado dentro do corpo do próprio lambda).

IMPORTANTE: embora as duas inclusões acima introduzam os poderes de expressar a
_seleção de caminhos de execução_ e de expressar repetições, através de
recursividade explícita. O poder computacional da linguagem na versão `v2` já
era Turing equivalente.

## 1. Léxico

Quatro novas palavras reservadas e dois novos operadores (as palavras
reservadas passam a ser sete).

```text
LETREC  ::=  letrec           ← NOVO (palavra reservada)
IF      ::=  if               ← NOVO (palavra reservada)
THEN    ::=  then             ← NOVO (palavra reservada)
ELSE    ::=  else             ← NOVO (palavra reservada)
EQEQ    ::=  ==               ← NOVO
LT      ::=  <                ← NOVO
```

Palavras reservadas: `let`, `in`, `fn`, `letrec`, `if`, `then`, `else`. As
demais categorias léxicas continuam existindo, da mesma forma que eram na
versão `v2`.

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

## 2. Sintaxe

Vale mais uma vez a observação sobre notação: os parênteses da _linguagem_ são
`LPAREN`/`RPAREN`; os parênteses `( … )` da EBNF são meta-símbolos.

Abaixo a EBNF atualizada de `aljabr` versão `v3`.

```text
exp     ::= let NOME = exp in exp
          | letrec NOME = fn LPAREN [ params ] RPAREN => exp in exp      ← NOVO
          | fn LPAREN [ params ] RPAREN => exp
          | if exp then exp else exp                                    ← NOVO
          | comp
comp    ::= soma [ ( == | < ) soma ]                                    ← NOVO
soma    ::= termo { ( + | - ) termo }          (antes, parte de exp)
termo   ::= fator { ( * | / ) fator }
fator   ::= unario [ ** fator ]
unario  ::= [ + | - ] chamada
chamada ::= atomo { LPAREN [ args ] RPAREN }
atomo   ::= INTEIRO | NOME | LPAREN exp RPAREN
params  ::= NOME { , NOME }
args    ::= exp { , exp }
```

Mudanças em relação à `v2`:
1. `exp` ganhou `letrec` e `if`;
2. nasceu o nível `comp` entre `exp` e `soma`;
3. o corpo que antes era de `exp` (`termo { (+|-) termo }`) passou a se chamar
   `soma`.

A gramática continua LL(1): `LETREC`, `IF`, `FN` e `LET` decidem a alternativa
de `exp`; `==` ou `<` decidem se `comp` tem o lado direito opcional.

### Exemplos de programas mal-formados

| Programa                               | Por quê                                         |
|----------------------------------------|-------------------------------------------------|
| `1 < 2 < 3`                            | `comp` não é associativa                        |
| `if x then 1`                          | `else` obrigatório                              |
| `letrec x = 5 in x`                    | o lado direito de `letrec` precisa ser `fn`     |
| `1 + if 1 then 2 else 3`               | `if` como operando sem parênteses               |
| `let if = 1 in if`                     | `if` é palavra reservada                        |


## 3. Semântica 

### Domínios semânticos: nenhuma mudança

| Domínio                                                                          | Descrição                                            |
|----------------------------------------------------------------------------------|------------------------------------------------------|
| $ℝ$                                                                              | Os números reais.                                    |
| $\mathrm{Clo} = \mathrm{Var}^* \times \mathrm{Exp} \times \mathrm{Env}$          | _Closures_: (parâmetros, corpo, ambiente de criação) |
| $\mathrm{Val} = ℝ ∪ \mathrm{Clo} ∪ \\{ \mathtt{erro} \\}$                        | Valores possíveis                                    |
| $\mathrm{Env} = \mathrm{Var} ⇀ \mathrm{Val}$                                     | Ambientes                                            |

$\mathrm{Val} = ℝ ∪ \mathrm{Clo} ∪
\\{\mathtt{erro}\\}$ (decisão A, opção 2). As comparações são operações
semânticas $f_{==}, f_{<} : ℝ \times ℝ \to \\{0, 1\\}$ e, como as demais, são
levadas a $\mathrm{Val}$ pelo _lift_ (closures em comparações dão `erro`).

### Condicional

Observe que só **um** caminho aparece nas premissas:

$$
\frac{
  \langle c, \rho \rangle \Downarrow n \quad (n \in ℝ,\ n \neq 0) \qquad
  \langle e_1, \rho \rangle \Downarrow v
}{
  \langle \texttt{if}\ c\ \texttt{then}\ e_1\ \texttt{else}\ e_2,\ \rho \rangle \Downarrow v
} \quad \text{(IfVerd)}
$$

$$
\frac{
  \langle c, \rho \rangle \Downarrow 0 \qquad
  \langle e_2, \rho \rangle \Downarrow v
}{
  \langle \texttt{if}\ c\ \texttt{then}\ e_1\ \texttt{else}\ e_2,\ \rho \rangle \Downarrow v
} \quad \text{(IfFalso)}
$$

$$
\frac{
  \langle c, \rho \rangle \Downarrow v_c \qquad v_c \in \mathrm{Clo}
}{
  \langle \texttt{if}\ c\ \texttt{then}\ e_1\ \texttt{else}\ e_2,\ \rho \rangle \Downarrow \mathbf{erro}
} \quad \text{(IfCond)}
$$

Se a condição avalia para `erro`, vale a convenção de propagação da Aula 12
§4.2. O caminho não escolhido **nunca é avaliado**, logo seus erros e sua
não-terminação nunca acontecem.

### Recursão

A regra define um ambiente em termos de si mesmo:

$$
\frac{
  \rho_1 = \rho[f \mapsto \mathsf{clo}((p_1, \ldots, p_n),\ e_f,\ \rho_1)]
  \qquad
  \langle e_2, \rho_1 \rangle \Downarrow v
}{
  \langle \texttt{letrec}\ f = \texttt{fn}\ (p_1, \ldots, p_n) \Rightarrow e_f\ \texttt{in}\ e_2,\ \rho \rangle \Downarrow v
} \quad \text{(LetRec)}
$$

Leitura: a primeira premissa não é uma avaliação, é uma **equação** que
descreve $\rho_1$. Ele é o ambiente em que $f$ já existe e é o closure de $f$
cujo ambiente de criação é... o próprio $\rho_1$. Logo, quando o corpo de $f$
procura $f$, encontra.

> **Retomada de observação da Aula 12 (§4.1)** Lá dissemos que closures são
> construídos "de dentro para fora" e que isso voltaria com a recursão. Aqui
> o ciclo é **genuíno**: o ambiente contém o closure, que contém o ambiente.
> (Tecnicamente, $\rho_1$ é um ponto fixo; não precisamos desse formalismo.)
>
> Nenhuma outra regra muda. Em particular, (App) continua avaliando o corpo
> em $\rho_0[\ldots]$: é o fato de $\rho_0 = \rho_1$ conter $f$ que faz a
> recursão funcionar.

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

#### Regras de definição e aplicação de funções (herdadas de aljabr v2)

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
