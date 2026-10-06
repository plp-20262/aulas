# Aula 08 — 04/Out — Estágio 3 (Semana 2)

## Retomando da aula (e do Estágio) anterior

Na aula passada, retomamos o foco em semântica. Formalizamos a especificação da
semântica de nossa segunda linguagem `calc`, usando semântica de avaliação (ou
semântica natural ou ainda semântica operacional de passo grande). 

Optamos por usar a notação $⟨e, ρ⟩ ⇓ v$, denominada um _julgamento_, que
expressa que o significado da expressão $e$, sob o ambiente $ρ$, é o valor $v$.
Vimos também que definimos como domínios semânticos (os conjuntos de dados
usados para expressar qualquer estado da computação) os conjuntos:
$\mathrm{Val}$ de valores que une os valores propriamente válidos dos domínios
de interesse adicionados ao valor de $\mathrm{erro}$; e $\mathrm{Env}$ o
conjunto de possíveis ambientes que, por sua vez, são mapas de nomes de
variáveis para valores.

Apresentamos as regras de avaliação na notação de lógica para dedução natural
conhecida por notação Gentzen em que temos premissas e conclusões, tipicamentes
expressas acima e abaixo de uma linha (com o nome da regra do lado direito).
Defimos cinco regras para uma versão simples de `calc`: $\mathrm{Num}$,
$\mathrm{Op}$, $\mathrm{DivZero}$, $\mathrm{ErrEsq}$ e $\mathrm{ErrDir}$.

Por fim, vimos como essas regras podem ser interpretadas como especificações
quase que literais de uma função `eval()` recursiva. Razão pela qual a própria
função tem assinatura semelhante à dos julgamentos: `eval(ast: Ast, env:
Environment) -> Val`.

Em `aula-08/calc-v4` apresento uma pequena, e última, atualização de `calc`.
Adicionei operadores unários e uma função de _lift_ para evelar as operações
parciais do domínio para operações totais. Com isso, é possível reduzir as
regras de tratamento de erro. Revise a definição formal de `calc-v4` no
[README.md](calc-v4/README.md) do diretório de `calc-v4`.

> Detalhe: em nossa LP, escolhemos que `-2 ** 2` deve ser interpretada como
> `(-2) ** 2`. Compare isso com Python em que a mesma expressão é interpretada
> como `-(2 ** 2)`.

## Nossa nova Linguagem: `aljabr` = `calc` + variáveis

O que são variáveis? Como são especificadas? Como são implementadas?

Há múltiplas formas possíveis de introduzir _variáveis_ em uma LP. Aqui, vamos
optar por uma sintaxe específica conhecida por `let..in`. Ela permite
introduzir variáveis, sem introduzir (ainda) estado explícito ou mutabilidade.
É usada por linguagens como OCAML, Haskell, Scheme, Racket, F#, Clojure e
Scala, para nomear apenas algumas.

### Visão geral da sintaxe e semântica da linguagem

A sintaxe abstrata é `let <var> = <exp1> in <exp2>`. E a semântica é que se
trata de uma expressão cujo valor reultante é o valor de `<exp2>` em que todas
as referências à variável `<var>` terão os valores avaliados como o valor da
avaliação de `<exp1>`. 

Em termos semântics, trata-se de uma variável local, com escopo delimitado à
própria expressão em que está definida. 

**Exemplo 1**. Queremos poder escrever programas como este. Observe que optamos
por escrevê-lo em duas linhas, apenas por legibilidade.

```python
let x = 10 in
(x - 1) * (x + 1)
```

O programa acima será avaliado como `(10 - 1) * (10 + 1)`, já que as
referências à variável `x` serão substituídas pelo valor `10` determinado pela
primeira linha.

**Exemplo 2**. Observe que na expressão ao lado direito da vinculação podemos
usar uma expressão qualquer. Logo, também poderemos escrever programas assim:

```javascript
let x = 3 * 3 + 1 in
(x - 1) * (x + 1)
```

**Exemplo 3**. Por fim, observe que cada `let..in` é uma expressão e pode ser
usada como uma das sub-expressões propostas pela sintaxe. Logo, pela própria
definição poderemos aninhar as definições e usar múltiplas variáveis assim:

```javascript
let x = 10 in
let y = x + 1 in
let z = x - 1 in
x + y * z
```

No programa acima, o primeiro `let` define `x` que é usado nas duas expressões
seguintes que definem `y` e `z`. Por fim, a expressão final dá o resultado a
ser produzido por todo o programa, usando as variáveis `x`, `y` e `z`.


## Especificação da Sintaxe

### Sintaxe Abstrata Estendida

A gramática abstrata de `calc-v2` ganha duas produções:

```python
exp ::= INTEIRO                    (número inteiro)
      | NOME                       (identificador/variável)     ← NOVA SINTAXE
      | let NOME = exp1 in exp2    (vinculação local)           ← NOVA SINTAXE
      | exp1 + exp2                (soma)
      | exp1 - exp2                (subtração)
      | exp1 * exp2                (multiplicação)
      | exp1 / exp2                (divisão inteira)
      | exp1 ** exp2               (divisão inteira)
      | + exp1                     (divisão inteira)
      | - exp1                     (divisão inteira)
      | (exp)                      (parênteses)
```

### Sintaxe concreta estendida

Abaixo registro a versão sintaxe concreta que usaremos pra construir nosso
parser descendente recursivo. Observe que apenas duas produções foram
adicionadas a duas das regras sintáticas, em comparação com a sintaxe da última
versão de `calc`.

```python
exp   ::= let ID = exp in exp                      ← NOVA SINTAXE
        | termo { ( + | - ) termo }
termo ::= fator { ( * | / ) fator }
fator ::= unario [ ** fator ]
unario::= [ + | - ] atomo
atomo ::= INTEIRO 
        | NOME                                     ← NOVA SINTAXE
        | ( exp )            
```

**Precedência** Observe que em termos da hierarquia de precedência dos
operadores, o `let` foi colocado no mesmo nível de `exp` e, portanto, com menor
precedência que `+` e `-`.

**Aninhamento** Observe que a produções de `exp` permitem aninhar `let..in`
recursivamente, de forma que a linguagem suporta o uso de múltiplas variáveis
sem nenhum problema. Note também que o uso de parênteses para o aninhamento é
opcional.

**Palavras reservadas** Observe ainda que precisaremos "reservar" palavras para
esta linguagem: `let` e `in` não poderão ser usadas como nomes de variáveis.


## Semântica

## Domínios semânticos

Aqui não há qualquer mudança em relação a `calc`. Os exatos mesmos domínios
semânticos são necessários: $\mathrm{Val}$ o conjunto de valores e
$\mathrm{Env}$ o conjunto de ambientes. Também precisaremos do conjunto
(categoria sintática) $\mathrm{Var}$ dos possíveis valores de variáveis.

Em geral, quando tratamos o assunto formalmente, denotamos ambientes pela letra
$ρ$. Como $ρ: \mathrm{Var} ⇀ \mathrm{Val}$, podemos expressar por $ρ(x)$ o
valor de $x$ no ambiente $ρ$. Também usaremos a notação $ρ[x ↦ v]$ para
expressar um ambiente derivado do ambiente $ρ$ mas em que a variável $x$ é
mapeada para o valor $v$.

```math
\rho[x \mapsto v](y) =
\begin{cases}
v & \text{se } y = x \\
\rho(y) & \text{caso contrário}
\end{cases}
```

> É conveniente usarmos uma versão _lifted_ de $ρ$ que retorna $\mathrm{erro}$
> para qualquer variável que não exista em $ρ$. Isso, mais uma vez, simplifica
> as regras de inferência, para os casos de uso de variáveis não definidas.

Na implementação, `ρ` pode ser modelado como um dicionário Python (ou lista de
dicionários, para escopos aninhados). Nesse caso, a operação `ρ[x ↦ v]`
corresponde a uma **cópia estendida** do dicionário. Observe que não há mutação
do ambiente original, preservando uma semântica funcional.


### Novas Regras de Avaliação

#### Variável

$$
\frac{\rho(x) = v}{\langle x, \rho \rangle \Downarrow v} \quad \text{(Var)}
$$

Se o ambiente associa `x` a `v`, então `x` avalia para `v`.

#### Variável Não Vinculada (Erro)

$$
\frac{x \notin \mathrm{dom}(\rho)}{\langle x, \rho \rangle \Downarrow \mathbf{erro}} \quad \text{(VarNaoLigada)}
$$

Se `x` não está no domínio de `ρ`, a avaliação resulta em `erro`. Isso
generaliza o tratamento de erro já presente em `calc-v2`.

> **Importante** Se optarmos por usar a versão _lifted_ de $ρ$, esta regra é
> desnecessária, já que o valor de $ρ(x)$ é $\mathrm{erro}$ quando $x$ não
> estiver no domínio de $ρ$.

#### Vinculação Local (`let`)

$$
\frac{
  \langle e_1, \rho \rangle \Downarrow v_1 \qquad
  \langle e_2, \rho[x \mapsto v_1] \rangle \Downarrow v_2
}{
  \langle \text{let } x = e_1 \text{ in } e_2, \rho \rangle \Downarrow v_2
} \quad \text{(Let)}
$$

Ou seja, para avaliar `let x = e1 in e2`:

1. avaliamos `e1` no ambiente **corrente** `ρ`, obtendo `v1`;
2. avaliamos `e2` no ambiente **estendido** `ρ[x ↦ v1]`, obtendo `v2`;
3. o resultado é `v2`.

Observe que:

- o ambiente `ρ` **não é modificado**: `ρ[x ↦ v1]` é uma nova função;
- `e1` é avaliada **antes** de `x` ser vinculada, portanto `x` **não** está em
escopo dentro de `e1` (o `let` **não é recursivo**);
- o escopo de `x` é **estritamente** o corpo `e2`.


### Escopo Léxico e Sombreamento (Shadowing)

Como `ρ[x ↦ v]` **sobrescreve** a associação de `x` quando ela já existe, a
nova associação **esconde** a antiga dentro do corpo. Considere:

```
let x = 1 in (let x = 2 in x) + x
```

- A ocorrência de `x` no `let` interno refere-se ao valor `2`;
- A ocorrência de `x` fora do `let` interno (mas dentro do `let` externo) refere-se ao valor `1`;
- Resultado: `2 + 1 = 3`.

Este comportamento corresponde ao que chamamos de **escopo léxico** (que também
pode ser chamado de _estático_), no qual cada ocorrência de uma variável é
resolvida pelo `let` mais próximo **sintaticamente** que a vincula.

### Exemplo de Derivação

Considere `let x = 2 + 3 in x * x` com ambiente inicial `ρ = ∅`.

```
⟨let x = 2 + 3 in x * x, ρ⟩ ⇓ 25        (Let)
├─ ⟨2 + 3, ρ⟩ ⇓ 5                       (Op)
│  ├─ ⟨2, ρ⟩ ⇓ 2                        (Num)
│  ├─ ⟨3, ρ⟩ ⇓ 3                        (Num)
│  └─ +↑(2, 3) = 5                      (operação semântica)
└─ ⟨x * x, ρ[x ↦ 5]⟩ ⇓ 25               (Op)
   ├─ ⟨x, ρ[x ↦ 5]⟩ ⇓ 5                 (Var)
   │  └─ ρ[x ↦ 5](x) = 5                (acesso ao ambiente)
   ├─ ⟨x, ρ[x ↦ 5]⟩ ⇓ 5                 (Var)
   │  └─ ρ[x ↦ 5](x) = 5                (acesso ao ambiente)
   └─ *↑(5, 5) = 25                     (operação semântica)
```

### Exemplo com Sombreamento

Considere `let x = 1 in (let x = 2 in x) + x` com ambiente inicial `ρ = ∅`.

```
⟨let x = 1 in (let x = 2 in x) + x, ρ⟩ ⇓ 3        (Let)
├─ ⟨1, ρ⟩ ⇓ 1                                     (Num)
└─ ⟨(let x = 2 in x) + x, ρ[x ↦ 1]⟩ ⇓ 3           (Op)
   ├─ ⟨let x = 2 in x, ρ[x ↦ 1]⟩ ⇓ 2              (Let)
   │  ├─ ⟨2, ρ[x ↦ 1]⟩ ⇓ 2                        (Num)
   │  └─ ⟨x, ρ[x ↦ 1][x ↦ 2]⟩ ⇓ 2                 (Var)
   │     └─ ρ[x ↦ 1][x ↦ 2](x) = 2                (acesso ao ambiente)
   ├─ ⟨x, ρ[x ↦ 1]⟩ ⇓ 1                           (Var)
   │  └─ ρ[x ↦ 1](x) = 1                          (acesso ao ambiente)
   └─ +↑(2, 1) = 3                                (operação semântica)
```

### Exemplo com Variável Livre

Considere `let x = 1 in x + y` com ambiente inicial `ρ = ∅`.

```
⟨let x = 1 in x + y, ∅⟩ ⇓ erro               (Let)
├─ ⟨1, ∅⟩ ⇓ 1                                (Num)
└─ ⟨x + y, ∅[x ↦ 1]⟩ ⇓ erro                  (ErrDir)
   ├─ ⟨x, ∅[x ↦ 1]⟩ ⇓ 1                      (Var)
   │  └─ ∅[x ↦ 1](x) = 1                     (acesso ao ambiente)
   └─ ⟨y, ∅[x ↦ 1]⟩ ⇓ erro                   (VarNaoLigada)
      └─ y ∉ dom(∅[x ↦ 1]) = {x}             (acesso ao ambiente)
```

### Pureza e Ausência de Efeitos

Apesar da introdução de variáveis, a linguagem **permanece puramente expressiva**:

- não há comandos de atribuição (`x := e`); há comando de ligação/vinculação;
- não há sequenciamento (`e1; e2`);
- não há laços nem condicionais nesta versão;
- a única forma de alterar o ambiente é o `let`, que produz um **novo** ambiente, sem mutação.

Isso preserva a **composicionalidade** da semântica: o valor de `let x = e1 in
e2` depende apenas do valor de `e1` e do valor de `e2` no ambiente estendido.
Também preserva o **determinismo**: a semântica continua sendo uma função
parcial de expressões (e ambientes) para valores.


### Propriedades Atualizadas

- **Determinismo**: mantém-se. Para toda expressão `e` e todo ambiente `ρ`,
existe no máximo um `v` tal que `⟨e, ρ⟩ ⇓ v`.
- **Composicionalidade**: mantém-se. O valor de uma expressão é função dos
valores de suas subexpressões imediatas (e do ambiente, para as variáveis).
- **Ambiente agora relevante**: o valor de uma expressão passa a depender de
`ρ` sempre que houver variáveis livres. `calc-v2` era o caso degenerado em que
`ρ` era irrelevante.
- **Ausência de recursão**: o `let` é **não-recursivo** (`let x = e1 in e2`):
`x` **não** está em escopo dentro de `e1`. Isso reflete a ordem de avaliação:
`e1` é avaliado **antes** da vinculação.


## Referências

- Material de semântica operacional big-step (semântica natural), baseado na formulação de Gilles Kahn.
- Implementação de referência: `calc-v2/` no repositório da disciplina.
- Nielson & Nielson, *Semantics with Applications: A Formal Introduction*;
capítulo sobre semântica natural, para o tratamento de `let` e ambientes.

