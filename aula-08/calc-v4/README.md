# Nova especificação de `calc`

Principais mudanças na especificação da LP:

- `calc` agora inclui operadores `-` e `+` unários;
- a especificação é baseada em operações semânticas totais (_lifted_);
- o _lift_ permite eliminar/simplificar regras de erro.

## Sintaxe

### Conceitual, idealizada

```python
exp    ::= exp + termo | exp - termo | termo
termo  ::= termo * fator | termo / fator | fator
fator  ::= unario ** fator | unario
unario ::= + atomo | - atomo | atomo
atomo  ::= INTEIRO | ( exp )
```

### EBNF efetiva usada

```python
exp     ::= termo { ( + | - ) termo }
termo   ::= fator { ( * | / ) fator }
fator   ::= unario [ ** fator ]
unario  ::= [ + | - ] atomo
atomo   ::= INTEIRO | ( exp )
```

> Esta gramática permite `+` e `-` unários, mas diferente de Python, não
> permite repetições. Para aceitar, poderíamos ter usado repetição explícita ou
> recursão à direita após o terminal e uma alternativa para permitir só um
> átomo: `unario ::= ( + | - ) unario | atomo`.


### AST

- precedência de operadores: `**` > `*`, `/` > `+`, `-`
- os operadores binários `+`, `-`, `*` e `/` são associativos à esquerda
- o operador `**` é associativo à direita
- os operadores unários `-` e `+` têm precedência mais alta que `**`

Como optamos por uma gramática em EBNF e uma implementação de referência com um
parser descendente recursivo, precisamos fazer nossa gramática ser LL(1) e,
portanto, sem recursões à esquerda. Apesar disso, a linguagem exige as
associatividades acima indicadas.


## Semântica Operacional Big-Step de `calc-v2`

### Domínios Semânticos

| Domínio                                       | Descrição                                                                  |
|-----------------------------------------------|----------------------------------------------------------------------------|
| $ℝ$                                           | Os números reais.                                                          |
| $\mathrm{Val} = ℝ ∪ \\{ \mathtt{erro} \\}$    | *Os valores possíveis*: os reais ou o valor especial `erro`                |
| $\mathit{Env} = \mathit{Var} ⇀ \mathit{Val}$  | Domínio dos ambientes (estado semântico)                                   |

> **Nota:** `Var` é o conjunto (infinito) de identificadores válidos da linguagem.


### Operações Semânticas e Operadores

Para simplificar as regras de inferência, usarei apenas operações semânticas
totais, obtidas através de um _lift_. Ou seja, as operações retornarão
$\mathrm{erro}$ para todo valor do domínio em que a original está indefinida.
As funções lifted também devem propagar erros em estilo monádico. Esta decisão
permite eliminar as regras de inferência para lidar com erros de funções
parciais e as regras de propação de erro.

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


### Exceções

Com a adoção da ideia acima, precisaremos criar regras específicas apenas para
situações julgadas excepcionais em que se queira valor resultante específico
diferente de $\mathrm{erro}$. Por exemplo, o valor de $0 ** 0$ é, em alguns
cenários da matemática, considerado igual a $0$ e em outros igual a $1$. Uma
regra específica pode ser usada apenas para garantir a clara e deliberada
especificação do valor que se deseja implementar na linguagem.


### Regras de Avaliação

#### Números

$$
\frac{}{\langle n, \rho \rangle \Downarrow n} \quad \text{(Num)}
$$


#### Operações Aritméticas

Para cada operador binário `Op ∈ {+, -, *, /, **}`:

$$
\frac{
  \langle e_1, \rho \rangle \Downarrow v_1 \qquad
  \langle e_2, \rho \rangle \Downarrow v_2 \qquad
  f_{\mathrm{Op}}^{\uparrow}(v_1,v_2) = v
}{
  \langle e_1 \text{ Op } e_2, \rho \rangle \Downarrow v
} \quad \text{(Op)}
$$


#### Divisão por Zero (Erro)

A adoção de operações semânticas totais que podem retornar $\mathrm{erro}$
torna a regra $\text{DivZero}$ da especificação anterior desnecessária. Perceba
que a função `eval()` poderá simplesmente retornar o resultado da operação
semântica $f_{÷}^{\uparrow}$ que, por ser _lifted_, já retorna o valor
$\mathrm{erro}$ que é um valor válido (confira a seção Domínios Semânticos). Ou
seja, $f_{÷}^{\uparrow}(n, 0) = \mathrm{erro}$ para qualquer valor $n \in ℝ$.


#### Propagação de Erro

Da mesma forma que a regra $\mathrm{DivZero}$, as regras $\mathrm{ErrEsq}$ e
${\mathrm{ErrDir}}$ também se tornaram desnecessárias com o uso das operações
_lifted_. Releia a definição da funções _lifted_ na seção _Operações Semânticas
e Operadores_, acima.
