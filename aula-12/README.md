## Aula 12 — 21/Out — Unidade 4: Funções e closures (parte 3/4)

> Tema da aula: conclusão da especificação formal de `aljabr` v2 (que difere de
> `v1` pela introdução de lambdas e closures). Também apresentarei, mais uma
> vez, uma visão geral de como essa especificação orientará a implementação.

## Objetivo geral

Na Aula 09 decidimos _como escrever_ funções em `aljabr` e vimos,
informalmente, _o que elas devem significar_: um lambda avalia para um
**closure**, que é uma tripla `(parâmetros, corpo, ambiente de criação)`. Na
aula passada, iniciamos a especificação formal da linguagem. Discutimos o novo
léxico e as novas regras sintáticas (nossa nova EBNF). Também discutimos as
consequências que essas decisões têm sobre nossa LP.

Nesta aula apresentarei as novas regras necessárias na especificação formal da
semântica e discutir como mapear essas especificaçãos (quase que) diretamente
para a implementação de nosso interpretador. As regras serão baseadas na
notação de _julgamentos_ no formato de regras com a notação $⟨e, ρ⟩ ⇓ v$
(lembre, ela expressa que o programa, ou expressão, $e$ quando avaliada no
ambiente $ρ$ avalia para o valor $v$). Relembre também que essa forma de
especificação de semântica é chamada de semântica natural (em referência à
dedução natural, da lógica) ou de semântica operacional de passo grande (em
referência ao fato de que cada regra diz diretamente qual o valor final
produzido por cada expressão).

## Bloco 1: Retomada e o que muda no pipeline

- ainda a escrever
- é necessário? aula há apenas 2 dias
- IDEIA: talvez retomar o uso de _tabelas de rastreamento_ para execução
  informal de programas de `aljabr-v2`
  - isto pode conectar bem com as regras e as derivações formais adiante

## Bloco 4: Semântica

### 4.1 Domínios semânticos

Até a versão `v1` de `aljabr`, temos os seguintes domínios semânticos: _números_, que são
os valores principais sobre os quais queremos computações; _valores_ que combina os números
e o valor `erro` formando o conjunto de valores que podem; e _ambientes_ que é o conjunto
dos possíveis mapeamentos de valores de variáveis a valores. Para a versão `v2`, com a 
inclusão de lambdas e aplicações, precisaremos de duas mudanças: 1) adicionar o
conjunto de _closures_ $\mathrm{Clo}$, que são os valores propriamente ditos dos lambdas
durante a avaliação (ou execução); e 2) atualizar o conjunto de _valores_ $\mathrm{Val}$,
para incluir os _closures_.

| Domínio                                                                          | Descrição                                            |
|----------------------------------------------------------------------------------|------------------------------------------------------|
| $ℝ$                                                                              | Os números reais.                                    |
| $\mathrm{Clo} = \mathrm{Var}^* \times \mathrm{Exp} \times \mathrm{Env}$          | _Closures_: (parâmetros, corpo, ambiente de criação) |
| $\mathrm{Val} = ℝ ∪ \mathrm{Clo} ∪ \\{ \mathtt{erro} \\}$                        | Valores possíveis                                    |
| $\mathrm{Env} = \mathrm{Var} ⇀ \mathrm{Val}$                                     | Ambientes                                            |

Escreveremos um closure como $\mathsf{clo}((p_1, \ldots, p_n),\, e,\, \rho)$.

> **Nota.** A definição é aparentemente circular: ambientes contêm valores,
> valores incluem closures e closures contêm ambientes. Mas não há problema:
> todo closure contém um ambiente que _já existia_ quando o closure foi criado
> (o ambiente de criação). Closures são, portanto, construídos "de dentro para
> fora". Guarde essa observação: ela volta quando falarmos de recursão.

**Notação.** Para vincular vários parâmetros de uma vez, usaremos a extensão
sucessiva do ambiente:

$$
\rho[p_1 \mapsto v_1, \ldots, p_n \mapsto v_n]
= (\cdots(\rho[p_1 \mapsto v_1])[p_2 \mapsto v_2] \cdots)[p_n \mapsto v_n]
$$

Como antes, é um **novo** ambiente: `ρ` não é modificado.

### 4.2 Regras que já conhecemos

As regras abaixo não mudam. Elas foram repetidas aqui apenas para que este
arquivo seja autocontido. Duas ressalvas: 1) usamos o ambiente _lifted_, o que
nos permite dispensar a regra (VarNaoLigada) vista da Aula 08 (lembre que na
ocasião comentei isso em sala de aula; que usar o ambiente _lifted_ permite
simplificar as regras de derivação); e 2) adotamos uma convenção para a
propagação de erros.)

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

**Ambiente _lifted_.** Como na Aula 08, usamos uma versão _lifted_ de `ρ`: para
toda variável `x ∉ dom(ρ)`, definimos `ρ(x) = erro`. Assim, a regra ($\mathrm{Var}$)
cobre também as variáveis não vinculadas, e não precisamos de uma regra à parte para
isso.

**Convenção de propagação de erro.** As regras desta unidade descrevem apenas
o caso em que as premissas produzem valores "de verdade" (elementos de
$ℝ ∪ \mathrm{Clo}$). Para os demais casos, adotamos uma convenção, declarada
uma única vez, válida para todas as regras:

> se alguma premissa da forma $⟨e, ρ⟩ ⇓ v$ produz $v = \mathbf{erro}$, a regra
> não se aplica e a conclusão é $\mathbf{erro}$.

A convenção abrevia as regras de propagação que escrevíamos uma a uma na Aula
07 (`ErrEsq` e `ErrDir`), uma para cada construção. Ela é o equivalente formal
do tratamento monádico de erros da implementação: o erro interrompe a
avaliação assim que aparece (erros são **estritos**). Em particular,
`let x = 1/0 in 5` vale `erro`, e não `5`.

Sobram, portanto, apenas as regras em que um erro **nasce** da própria
construção, e não de uma operação (para as operações, o _lift_ já cuida disso).
É o caso da aplicação, que veremos a seguir.

### 4.3 Novas regras de avaliação

**Criação de closure.** Um lambda avalia para um closure que "congela" o
ambiente corrente:

$$
\frac{}{
  \langle \texttt{fn}\ (p_1, \ldots, p_n) \Rightarrow e,\ \rho \rangle
  \Downarrow
  \mathsf{clo}((p_1, \ldots, p_n),\ e,\ \rho)
} \quad \text{(Lam)}
$$

**Aplicação.** Este é o coração da aula:

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

**Leitura da regra (App)**:

Relembre que para ler regras de derivação é conveniente ler primeiro a regra da conclusão
(parte abaixo da linha), para sabermos o que queremos calcular. A conclusão indica qual é
a forma da expressão para a qual queremos saber o significado (ou resultado). E as premissas,
condições expressas acima da linha, determinam tudo o que precisamos garantir para ter o
direito de aceitar a conclusão.

Neste caso, a conclusão indica que a regra nos permitirá saber como avaliar uma expressão
na forma $e_f(a_1, \ldots, a_n)$ em um momento da computação em que o ambiente é $\rho$. Em
particular, poderemos aceitar que o significado ou o valor resultante da expressão é $v$.
Para isso, precisamos garantir que as premissas (condições acima da linha) sejam verdadeiras.
Nesta regra são exigidas três condições gerais.

A primeira premissa: $\langle e_f, \rho \rangle \Downarrow \mathsf{clo}((p_1, \ldots, p_n),
e_b, \rho_0)$ exige que a expressão que queremos aplicar, $e_f$, seja avaliada para um closure
no mesmo ambiente $\rho$ em que se quer fazer a aplicação. Ou seja, essa condição da regra
exige que $e_f$ expresse uma função. Relembre, contudo, que uma função é um _closure_: uma
tripla $\mathsf{clo}((p_1, \ldots, p_n), e_b, \rho_0)$ que consiste em uma sequência de
parâmetros $(p_1, \ldots, p_n)$, uma expressão $e_b$ e um ambiente de próprio (obtido da
definição do lambda) $\rho_0$. Observe que a premissa exige que haja exatamente $n$ parâmetros
que é exatamente o mesmo número $n$ de argumentos na aplicação (veja a forma da conclusão).

A segunda premissa: $\langle a_i, \rho \rangle \Downarrow v_i \quad (1 \le i \le n)$ é, na
verdade, um conjunto de $n$ premissas. Elas exigem que as $n$ expressões $a_i$
usadas como argumentos de chamada de $e_f$ sejam avaliadas para os valores $v_i$, no
mesmo ambiente $\rho$ em que está sendo feita a aplicação da conclusão.

Por fim, a terceira premissa: $\langle e_b, \rho_0[p_1 \mapsto v_1, \ldots, p_n \mapsto v_n]
\rangle \Downarrow v$ exige que a avaliação do corpo do closure $e_b$ seja avaliado para $v$,
no ambiente de criação do closure $\rho_0$ em que os parâmetrso $p_i$ tenham sido mapeados
para os valores $v_i$ a que correspondem os argumentos de chamada.

Em resumo, podemos dizer que a regra determina que, para avaliar a chamada de função $e_f(a_1, a_2, \ldots a_n)$, é 
necessário: 1) que a expressão $e_f$ seja avaliada para uma função (um closure, mais
especificamente); e 2) que os argumentos $a_i$ sejam avaliados para os valores $v_i$;
e 3) que o resultado da chamada da função $e_f(\ldots)$ será o valor da avaliação do corpo da função,
no ambiente próprio da função, com os valores dos parâmetros mapeados pros valores $v_i$.

> **Pergunta:** na regra (App), em qual ambiente é avaliada cada uma das
> três premissas?
>
> Resposta: a primeira e a segunda, em `ρ` (ambiente de chamada). A terceira,
> em `ρ₀[…]` (ambiente de criação estendido). É exatamente essa diferença que
> explica por que `soma_n(3)` vale `10` e não `103`.

A regra operacional, informal dada na Aula 09 (Seção 4.5) está toda aqui:

| Passo na Aula 09                           | Onde está na formalização                                            |
|--------------------------------------------|----------------------------------------------------------------------|
| 1. avaliar `f` em `ρ` ⟹ closure           | 1ª premissa de (App); (AppNaoFuncao) se não for closure              |
| 2. se `m ≠ n`, erro de aridade             | (AppAridade)                                                         |
| 3. avaliar cada `aᵢ` em `ρ` ⟹ `vᵢ`        | 2ª premissa de (App); erro em algum `aᵢ` ⟹ convenção de propagação  |
| 4. avaliar corpo em `ρ₀[p₁ ↦ v₁, …]`       | 3ª premissa de (App)                                                 |

### 4.4 Regras de erro da aplicação

Há duas maneiras de uma aplicação **originar** um erro, uma por regra. Os erros
que apenas se _propagam_ (um argumento que avalia para `erro`, ou um corpo que
resulta em `erro`) não precisam de regra própria: são cobertos pela convenção
da Seção 4.2 e pela própria regra (App), cujo valor é o valor do corpo.

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

### 4.5 Erros em ação

| Programa                                  | Resultado | Por quê                                                        |
|-------------------------------------------|-----------|----------------------------------------------------------------|
| `5(3)`                                    | `erro`    | (AppNaoFuncao): `5` não é closure                              |
| `let f = fn (x, y) => x + y in f(1)`      | `erro`    | (AppAridade): 2 parâmetros, 1 argumento                        |
| `let q = fn (x) => x in q + 1`            | `erro`    | (Op) com _lift_: closure não pertence a ℝ                      |
| `let f = fn (x) => x + y in f(1)`         | `erro`    | `ρ(y) = erro` (ρ lifted), propagado por (Op), só na chamada    |
| `let f = fn (x) => x + y in 10`           | `10`      | (Lam) não avalia o corpo; ninguém procurou `y`                 |
| `let x = 1/0 in 5`                        | `erro`    | convenção: a 1ª premissa de (Let) avalia para `erro`           |
| `(fn (x) => 5)(1/0)`                      | `erro`    | convenção: o argumento avalia para `erro`                      |

Os dois programas com `y` merecem atenção. Na primeira forma, `y` é uma
variável livre que não está em lugar nenhum. A lambda foi criada normalmente e
só quando o corpo é avaliado, na chamada, o erro aparece. Na segunda forma, a
lambda nunca é chamada e o programa vale `10`. **Criar uma função não executa o
seu corpo.**

Os dois últimos ilustram a convenção de propagação: o erro interrompe a
avaliação mesmo quando o valor com erro não seria usado (o resultado `5` não
depende de `x`). É o que significa dizer que os erros são estritos.


## Bloco 5: Derivações e propriedades

> Como na Aula 08, as derivações abaixo estão em árvore indentada: a conclusão
> na raiz e as premissas como filhos, na ordem em que aparecem na regra. As
> condições laterais (como `ρ(x) = v`) são folhas rotuladas.

### 5.1 Exemplo 1: `let quad = fn (x) => x * x in quad(3) + quad(5)`

```text
⟨let quad = fn (x) => x * x in quad(3) + quad(5), ∅⟩ ⇓ 34   (Let)
├─ ⟨fn (x) => x * x, ∅⟩ ⇓ Q                                 (Lam)
│     onde Q = clo((x), x * x, ∅)
└─ ⟨quad(3) + quad(5), ρ₁⟩ ⇓ 34                             (Op)
   │     onde ρ₁ = ∅[quad ↦ Q]
   ├─ ⟨quad(3), ρ₁⟩ ⇓ 9                                     (App)
   │  ├─ ⟨quad, ρ₁⟩ ⇓ Q                                     (Var)
   │  │  └─ ρ₁(quad) = Q                                    (acesso ao ambiente)
   │  ├─ ⟨3, ρ₁⟩ ⇓ 3                                        (Num)
   │  └─ ⟨x * x, ∅[x ↦ 3]⟩ ⇓ 9                              (Op)
   │     ├─ ⟨x, ∅[x ↦ 3]⟩ ⇓ 3                               (Var)
   │     │  └─ ∅[x ↦ 3](x) = 3                              (acesso ao ambiente)
   │     ├─ ⟨x, ∅[x ↦ 3]⟩ ⇓ 3                               (Var)
   │     │  └─ ∅[x ↦ 3](x) = 3                              (acesso ao ambiente)
   │     └─ *↑(3, 3) = 9                                    (operação semântica)
   ├─ ⟨quad(5), ρ₁⟩ ⇓ 25                                    (App)
   │  └─ ⋯ análoga à anterior, com x ↦ 5
   └─ +↑(9, 25) = 34                                        (operação semântica)
```

Observe que o corpo `x * x` é avaliado duas vezes, uma para cada aplicação,
cada vez em um ambiente diferente (`x ↦ 3` e `x ↦ 5`). Foi exatamente isso que
buscávamos ao abstrair a _computação_: uma única definição, vários usos.

### 5.2 Exemplo 2: `soma_n(3)` vale `10`

```text
let n = 7 in
let soma_n = fn (x) => x + n in
let n = 100 in
soma_n(3)
```

```text
⟨let n = 7 in … soma_n(3), ∅⟩ ⇓ 10                          (Let)
├─ ⟨7, ∅⟩ ⇓ 7                                               (Num)
└─ ⟨let soma_n = fn (x) => x + n in … soma_n(3), ρ₁⟩ ⇓ 10   (Let)
   │     onde ρ₁ = ∅[n ↦ 7]
   ├─ ⟨fn (x) => x + n, ρ₁⟩ ⇓ S                             (Lam)
   │     onde S = clo((x), x + n, ρ₁)
   └─ ⟨let n = 100 in soma_n(3), ρ₂⟩ ⇓ 10                   (Let)
      │     onde ρ₂ = ρ₁[soma_n ↦ S]
      ├─ ⟨100, ρ₂⟩ ⇓ 100                                    (Num)
      └─ ⟨soma_n(3), ρ₃⟩ ⇓ 10                               (App)
         │     onde ρ₃ = ρ₂[n ↦ 100]
         ├─ ⟨soma_n, ρ₃⟩ ⇓ S                                (Var)
         │  └─ ρ₃(soma_n) = S                               (acesso ao ambiente)
         ├─ ⟨3, ρ₃⟩ ⇓ 3                                     (Num)
         └─ ⟨x + n, ρ₁[x ↦ 3]⟩ ⇓ 10                         (Op)
            │     onde ρ₁[x ↦ 3] = { n ↦ 7, x ↦ 3 }
            ├─ ⟨x, ρ₁[x ↦ 3]⟩ ⇓ 3                           (Var)
            │  └─ ρ₁[x ↦ 3](x) = 3                          (acesso ao ambiente)
            ├─ ⟨n, ρ₁[x ↦ 3]⟩ ⇓ 7                           (Var)
            │  └─ ρ₁[x ↦ 3](n) = 7                          (acesso ao ambiente)
            └─ +↑(3, 7) = 10                                (operação semântica)
```

Compare esta árvore com o rastreamento passo a passo da Aula 09 (§4.6). É a
mesma história, agora escrita com regras:

- a lambda foi avaliada em `ρ₁` e o closure `S` guardou `ρ₁` (onde `n ↦ 7`);
- a aplicação aconteceu em `ρ₃` (onde `n ↦ 100`), e `ρ₃` foi usado para
  encontrar `soma_n` e avaliar o argumento `3`;
- o corpo, contudo, foi avaliado em `ρ₁[x ↦ 3]`, e não em `ρ₃[x ↦ 3]`.

### 5.3 Exemplo 3: um closure criado por outro closure

`(fn (x) => fn (y) => x + y)(2)(3)`, que já vimos na Aula 09 (§6.2).

```text
⟨(fn (x) => fn (y) => x + y)(2)(3), ∅⟩ ⇓ 5   (App)
├─ ⟨(fn (x) => fn (y) => x + y)(2), ∅⟩ ⇓ C   (App)
│  │     onde C = clo((y), x + y, ∅[x ↦ 2])
│  ├─ ⟨fn (x) => fn (y) => x + y, ∅⟩ ⇓ L     (Lam)
│  │     onde L = clo((x), fn (y) => x + y, ∅)
│  ├─ ⟨2, ∅⟩ ⇓ 2                             (Num)
│  └─ ⟨fn (y) => x + y, ∅[x ↦ 2]⟩ ⇓ C        (Lam)
├─ ⟨3, ∅⟩ ⇓ 3                                (Num)
└─ ⟨x + y, ∅[x ↦ 2][y ↦ 3]⟩ ⇓ 5              (Op)
   ├─ ⟨x, ∅[x ↦ 2][y ↦ 3]⟩ ⇓ 2               (Var)
   │  └─ ∅[x ↦ 2][y ↦ 3](x) = 2              (acesso ao ambiente)
   ├─ ⟨y, ∅[x ↦ 2][y ↦ 3]⟩ ⇓ 3               (Var)
   │  └─ ∅[x ↦ 2][y ↦ 3](y) = 3              (acesso ao ambiente)
   └─ +↑(2, 3) = 5                           (operação semântica)
```

Observe o closure `C`: ele foi criado quando `x` valia `2` e carrega essa
informação em seu ambiente de criação. Quando `C` é aplicado a `3`, o corpo
`x + y` encontra `x` (vindo de `ρ₀`) e `y` (vindo do argumento). Sem a captura
do ambiente, a lambda interna não poderia ser avaliada: o `x` teria
desaparecido junto com a aplicação que o ligou.

### 5.4 Exemplos de erro

Aplicando algo que não é função:

```text
⟨let a = 3 in a(4), ∅⟩ ⇓ erro   (Let)
├─ ⟨3, ∅⟩ ⇓ 3                   (Num)
└─ ⟨a(4), ρ₁⟩ ⇓ erro            (AppNaoFuncao)
   │     onde ρ₁ = ∅[a ↦ 3]
   ├─ ⟨a, ρ₁⟩ ⇓ 3               (Var)
   │  └─ ρ₁(a) = 3              (acesso ao ambiente)
   └─ 3 ∈ ℝ                     (condição lateral)
```

Número errado de argumentos:

```text
⟨let f = fn (x, y) => x + y in f(1), ∅⟩ ⇓ erro   (Let)
├─ ⟨fn (x, y) => x + y, ∅⟩ ⇓ F                   (Lam)
│     onde F = clo((x, y), x + y, ∅)
└─ ⟨f(1), ρ₁⟩ ⇓ erro                             (AppAridade)
   │     onde ρ₁ = ∅[f ↦ F]
   ├─ ⟨f, ρ₁⟩ ⇓ F                                (Var)
   │  └─ ρ₁(f) = F                               (acesso ao ambiente)
   └─ 1 ≠ 2                                      (condição lateral: nº de argumentos ≠ nº de parâmetros)
```

### 5.5 Propriedades

- **Determinismo.** Continua valendo para as novas regras: (App),
  (AppNaoFuncao) e (AppAridade) são mutuamente exclusivas, pois cada uma
  depende do valor de `e_f` e do número de argumentos. (E, pela convenção de
  propagação, as regras só se aplicam quando as premissas não produzem `erro`;
  os casos com erro têm uma única conclusão possível.)

- **Escopo léxico.** O valor de uma aplicação depende do closure e dos valores
  dos argumentos, **não** do ambiente em que a aplicação ocorre (além de ser
  nele que se encontram `f` e os argumentos). Foi isso que vimos no Exemplo 2:
  mudar `n` _depois_ de criar `soma_n` não afeta `soma_n`.

- **Funções ainda não podem chamar a si mesmas.** O `let` continua não
  recursivo (Aula 08): em `let f = e₁ in e₂`, `e₁` é avaliada em `ρ`, onde `f`
  ainda não existe. Logo, o closure de `f` não captura `f`:

  ```text
  let f = fn (n) => f(n) in f(1)     # erro: variável 'f' não vinculada
  ```

  Guarde essa limitação: voltaremos a ela.

- **Pureza.** Continuamos sem mutação: o único modo de alterar um ambiente é
  criar um novo, estendendo o anterior.


## Bloco 6: Da especificação à implementação

> Nesta seção, apenas o mapa. A implementação de referência será apresentada
> no início da Aula 12. Use este mapa para implementar você mesmo.

### 6.1 Léxico → lexer

| Especificação                          | Implementação                                             |
|----------------------------------------|-----------------------------------------------------------|
| três novas categorias léxicas          | três novos tipos de token e três novas entradas na lista de regras |
| `=>` antes de `=`                      | posição de `ARROW` na lista, antes de `EQUAL`             |
| `fn` é palavra reservada               | nova entrada no mapa de palavras reservadas               |

### 6.2 EBNF → parser

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

### 6.3 Regras de avaliação → eval

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

### 6.4 Conjunto de testes

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


