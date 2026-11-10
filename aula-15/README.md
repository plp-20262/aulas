# Aula 15 — 08/Nov — Unidade 5 (1/3)

Tema da aula: estado e mutação.

A partir desta unidade construiremos uma nova mini-linguagem que chamaremos de **Algora**. O nome faz referência a ser uma evolução _imperativa_ de Aljabr, aproximando-a da família Algol de linguagens.

Até aqui, em todas as linguagens que construímos, avaliar uma expressão não altera o mundo em que ela é avaliada. Uma expressão pode chamar funções, criar closures e até realizar recursão, mas jamais pode modificar um valor que será observado por chamadas posteriores.

Hoje vamos investigar o que precisamos mudar para permitir que uma variável mantenha dados entre diferentes momentos da execução.

## 1. O que falta a nosso contador?

Na aula anterior, discutimos um programa que gostaríamos de conseguir escrever:

```text
contador()  // --> 1
contador()  // --> 2
contador()  // --> 3
```

O aspecto importante deste programa não é simplesmente contar até três. É que **chamadas sucessivas a uma mesma função, sem argumentos, produzem resultados diferentes**.

Em Aljabr, podemos até escrever funções recursivas, mas isso não resolve o problema. Por exemplo:

```text
letrec contador =
  fn (n) =>
    if n == 0
    then 0
    else contador(n - 1)
in
  contador(3)
```

O programa Aljabr acima conta regressivamente. Mas observe que cada chamada à função `contador` recebe um argumento diferente. E se chamarmos novamente `contador(3)`, obteremos novamente o mesmo resultado.

O que falta é alguma forma de uma chamada deixar um dado que possa ser consultado ou modificado em uma chamada posterior.

<details>
<summary>Como poderíamos, por exemplo, implementar uma função que se lembre de quantas vezes já foi chamada?</summary>

Precisamos de alguma forma de armazenar uma informação que sobreviva ao término de uma chamada e que possa ser consultada e modificada por chamadas posteriores.

Uma possibilidade é manter uma variável `n`, inicialmente igual a zero, e incrementá-la a cada chamada. Para isso, precisamos de uma operação de atribuição que modifique o valor associado à variável, em vez de simplesmente criar uma nova vinculação.

</details>

### 1.1 Uma proposta

Uma possibilidade é criar uma variável `n`, inicializada com zero, e incrementá-la a cada chamada, com uma _atribuição_:

```text
n := n + 1
```

O problema é que isto exige duas capacidades que nossas linguagens ainda não têm:

- armazenar um valor que continue existindo depois que uma função termina;
- modificar esse valor sem criar uma nova variável independente.

Relembre da semântica de Aljabr, que `let x = exp1 in exp2` introduz a variável `x`, a vincula ao valor produzido por `exp1` e essa vinculação é usada exclusivamente em `exp2`. A vinculação tem escopo bem definido e não há qualquer alteração do valor associado. Leia o código abaixo. Ele não deve ser confundido com a atualização da variável no código que estamos propondo acima. No programa abaixo, há dois nomes `n` distintos, cada um com um valor associado: o primeiro vinculado a 1 e o segundo vinculado a 2. Nenhum dos valores é alterado em nenhum momento da execução.

```text
let n = 1 in
  (let n = n + 1 in
     n * 2) + n
```

<details>
<summary>Qual é o resultado dessa expressão? O valor associado ao primeiro `n` é modificado?</summary>

O resultado é `5`.

A expressão interna `let n = n + 1 in n * 2` cria uma nova vinculação para `n`. O lado direito dessa declaração utiliza o `n` externo, cujo valor é `1`, e produz `2`. O corpo da expressão interna calcula `2 * 2`, produzindo `4`.

Depois, somamos esse resultado ao `n` externo, que continua valendo `1`. Portanto, o resultado final é `4 + 1 = 5`.

Não houve modificação do primeiro `n`. Foram criadas duas vinculações distintas, cada uma com seu próprio valor.

</details>

## 2. Onde ficará guardada a informação?

Uma primeira proposta de implementação poderia ser aproveitar o próprio ambiente de execução.

Lembremos que, em nosso interpretador, o ambiente associa nomes a valores. Podemos representá-lo, de maneira simplificada, por um dicionário:

```python
ambiente = {
    "x": 10,
    "y": 20,
}
```

Então é fácil imaginar que uma atribuição poderia simplesmente atualizar esse dicionário:

```python
ambiente["x"] = 30
```

Assim, uma consulta posterior a `x` encontraria o valor `30`.

Essa é uma proposta perfeitamente razoável e parece resolver o problema inicial: podemos modificar o ambiente e observar a mudança em consultas posteriores.

Mas vamos pensar em outra situação.

### 2.1 Dois nomes, uma informação

Imagine que dois nomes diferentes possam se referir à mesma variável:

```text
a := alguma_coisa
b := a
```

Se modificarmos o valor associado a `a`, o que deve acontecer com `b`?

<details>
<summary>Há pelo menos duas interpretações possíveis. Quais são elas?</summary>

1. `b` recebe uma cópia do valor de `a`; mudanças posteriores em `a` não afetam `b`.
2. `b` passa a se referir à mesma variável que `a`; mudanças feitas por um nome são observadas pelo outro.

A primeira interpretação trata a declaração de `b` como uma cópia do valor atual. A segunda faz com que ambos os nomes compartilhem a mesma variável.

</details>

A segunda possibilidade é especialmente interessante. Ela permite que diferentes partes de um programa compartilhem uma mesma informação mutável.

Para representar isso com clareza, vamos separar duas coisas que até agora estavam juntas: **os nomes e os valores armazenados**.

## 3. Ambiente e store

Vamos introduzir duas estruturas conceituais.

- O **ambiente** associa nomes a localizações de memória.
- O **store** associa localizações de memória aos valores armazenados nelas.

Usaremos as seguintes notações:

$$
\rho : \text{Nome} \longrightarrow \text{Localização}
$$

$$
\sigma : \text{Localização} \longrightarrow \text{Valor}
$$

A letra grega $\rho$ (rho) representa o ambiente; $\sigma$ (sigma) representa o store.

Por exemplo, considere:

$$
\rho =
\begin{cases}
x \mapsto \ell_1\\
y \mapsto \ell_2
\end{cases}
\qquad
\sigma =
\begin{cases}
\ell_1 \mapsto 10\\
\ell_2 \mapsto 20
\end{cases}
$$

O nome `x` não está diretamente associado ao valor `10`. Ele está associado à localização $\ell_1$, onde encontramos o valor `10`.

Podemos visualizar a situação assim:

```text
        ambiente (ρ)              store (σ)

       x ────────────────> ℓ₁ ─────────> 10

       y ────────────────> ℓ₂ ─────────> 20
```

A separação parece um detalhe de implementação, mas abre possibilidades importantes.

Se quisermos descobrir o valor associado a `y`, primeiro, consultamos o ambiente para descobrir a localização associada a `y`:

$$
\rho(y) = \ell_2
$$

Depois, consultamos o store para descobrir o valor armazenado nessa localização:

$$
\sigma(\ell_2) = 20
$$

Portanto, o valor de `y` é `20`.

### 3.1 Modificar um valor

Se modificarmos o valor armazenado em $\ell_1$, o ambiente não precisa mudar:

$$
\sigma_1 = \sigma[\ell_1 \mapsto 30]
$$

O resultado será:

```text
        ambiente (ρ)              store (σ')

       x ────────────────> ℓ₁ ─────────> 30

       y ────────────────> ℓ₂ ─────────> 20
```

O nome `x` continua associado à mesma localização. O que mudou foi o conteúdo dessa localização.

Essa é a ideia central da mutação: **a localização permanece, mas o valor nela armazenado pode mudar**.

O que precisou mudar para que o valor de `x` passasse de 10 para 30? Observe que o ambiente continua associando `x` à localização $\ell_1$. Apenas o store foi atualizado:

$$
\sigma_1 = \sigma[\ell_1 \mapsto 30]
$$

A localização permanece a mesma; seu conteúdo é que foi modificado.


### 3.2 Criar uma variável

E como uma variável passa a existir?

Vamos adotar, inicialmente, uma decisão simples: toda variável é declarada já com um valor inicial.

Por exemplo:

```text
var x := 10
```

Essa declaração realiza três operações conceituais:

1. avalia a expressão inicial, obtendo o valor `10`;
2. cria uma nova localização, digamos $\ell_3$;
3. associa `x` a $\ell_3$ no ambiente e armazena `10` nessa localização.

Formalmente, se $\ell_3$ for uma localização nova:

$$
\rho_1 = \rho[x \mapsto \ell_3]
$$

$$
\sigma_1 = \sigma[\ell_3 \mapsto 10]
$$

Não estamos introduzindo variáveis que existem sem valor inicial. Isso evita, por enquanto, a necessidade de definir um valor padrão ou um estado especial de variável não inicializada.

Compare:

| Construção | O que acontece? |
|---|---|
| `var x := 10` | Cria uma localização, associa `x` a ela e armazena `10`. |
| `x := 20` | Atualiza o valor na localização já associada a `x`. |

A primeira cria uma variável; a segunda modifica o valor de uma variável existente.

<details>
<summary>Por que não tratamos `var x := 10` simplesmente como uma atribuição?</summary>

Porque as duas construções têm responsabilidades diferentes.

A declaração precisa criar uma nova localização e estender o ambiente, associando o nome `x` a essa localização. A atribuição pressupõe que a variável já existe: ela encontra a localização por meio do ambiente e modifica apenas o valor armazenado nela.

</details>

## 4. Como a avaliação muda?

Até aqui, nossa avaliação de expressões podia ser descrita, de maneira simplificada, assim:

$$
\langle e,\rho\rangle \Downarrow v
$$

Lemos: avaliar a expressão $e$, no ambiente $\rho$, produz o valor $v$.

Agora precisamos considerar também o store. Avaliar uma expressão pode modificar valores armazenados.

Vamos usar:

$$
\langle e,\rho,\sigma\rangle
\Downarrow
\langle v,\sigma_1\rangle
$$

Lemos: avaliar a expressão $e$, no ambiente $\rho$ e no store $\sigma$, produz o valor $v$ e um novo store $\sigma_1$.

Observe que o ambiente permanece o mesmo nessa avaliação. A criação de novas variáveis, que modifica o ambiente, será tratada como uma construção própria da linguagem.

### 4.1 Consultar uma variável

Quando avaliamos uma variável, fazemos duas consultas:

1. procuramos no ambiente a localização associada ao nome;
2. procuramos no store o valor armazenado nessa localização.

A regra pode ser escrita assim:

$$
\frac{
\rho(x)=\ell
\qquad
\sigma(\ell)=v
}{
\langle x,\rho,\sigma\rangle
\Downarrow
\langle v,\sigma\rangle
}
$$

A avaliação de `x` não modifica o store. Apenas consulta a localização e seu conteúdo. E por que o store que aparece no resultado da regra é o mesmo store que aparece na entrada? Porque **consultar uma variável não modifica o estado da execução**. A avaliação apenas consulta o ambiente para encontrar a localização e, em seguida, consulta o store para obter o valor. Assim, o resultado é o mesmo store que tínhamos inicialmente:

$$
\sigma_1 = \sigma
$$


### 4.2 Atribuir um novo valor

Considere:

```text
x := 30
```

A atribuição deve:

1. encontrar a localização associada a `x`;
2. avaliar a expressão à direita da atribuição;
3. atualizar o store naquela localização.

<details>
<summary>O que essa construção produz como resultado? Apenas modifica o store ou também produz um valor?</summary>

Essa é uma decisão de design da linguagem. Para começar, vamos adotar a seguinte escolha: uma atribuição produz o valor que foi atribuído.

Assim, se `x := 30` for avaliada, o resultado será `30`, e o store será atualizado.

Outras linguagens poderiam fazer a atribuição produzir um valor especial, ou simplesmente não produzir valor algum. Voltaremos à distinção entre expressões e comandos na próxima aula.

</details>

A regra fica:

$$
\frac{
\rho(x)=\ell
\qquad
\langle e,\rho,\sigma\rangle
\Downarrow
\langle v,\sigma_1\rangle
}{
\langle x := e,\rho,\sigma\rangle
\Downarrow
\langle v,\sigma_1[\ell\mapsto v]\rangle
}
$$

<details>
<summary>Por que usamos $\sigma_1$, em vez de simplesmente $\sigma$, na conclusão?</summary>

Porque a própria expressão à direita da atribuição pode modificar o store. Primeiro avaliamos essa expressão; depois atualizamos a localização de `x`.

Por exemplo, se a expressão à direita realizar alguma outra atribuição, precisamos preservar as alterações que ela produziu. O store resultante da avaliação da expressão é $\sigma_1$, e é sobre ele que fazemos a atualização final.

</details>

## 5. Compartilhamento e aliasing

Agora podemos representar uma situação que seria difícil de expressar com clareza se nomes estivessem diretamente associados a valores.

Suponha que dois nomes estejam associados à mesma localização:

$$
\rho =
\begin{cases}
a \mapsto \ell_1\\
b \mapsto \ell_1
\end{cases}
\qquad
\sigma =
\begin{cases}
\ell_1 \mapsto 10
\end{cases}
$$

Visualmente:

```text
        ambiente (ρ)              store (σ)

       a ───────┐
                ├────────> ℓ₁ ─────────> 10
       b ───────┘
```

Se executarmos:

```text
a := 50
```

o store passa a conter:

$$
\sigma_1 =
\begin{cases}
\ell_1 \mapsto 50
\end{cases}
$$

<details>
<summary>Qual será o valor encontrado quando consultarmos `a`? E quando consultarmos `b`?</summary>

Os dois nomes produzirão `50`.

O ambiente continua associando ambos à mesma localização $\ell_1$. Como o valor armazenado nessa localização foi atualizado para `50`, qualquer consulta que chegue a $\ell_1$ encontrará esse novo valor.

</details>

Tanto `a` quanto `b` passam a encontrar o valor `50`, pois ambos apontam para a mesma localização.

Essa situação é chamada de **aliasing**: nomes diferentes são associados à mesma localização.

O aliasing é uma consequência importante da separação entre ambiente e store. Ele permite compartilhamento, mas também exige atenção: uma parte do programa pode modificar um valor que outra parte utiliza.

## 6. Voltando ao contador

Agora temos os ingredientes que faltavam.

Podemos criar uma função que tenha acesso a uma variável e que, a cada chamada, modifique o valor armazenado nessa variável.

A sintaxe abaixo é apenas uma ilustração inicial de como isso poderia aparecer em Algora:

```text
function criaContador() {
    var n := 0;

    return function() {
        n := n + 1;
        return n;
    };
}

var c := criaContador();

c(); // 1
c(); // 2
c(); // 3
```

<details>
<summary>O que acontece durante a criação e as chamadas do contador?</summary>

1. `criaContador` cria uma variável `n`, inicialmente com valor zero.
2. A função interna captura o ambiente no qual foi criada.
3. Esse ambiente associa `n` a uma localização no store.
4. Cada chamada de `c` atualiza o valor armazenado nessa localização.
5. Como as chamadas compartilham a mesma localização, cada uma observa o resultado da chamada anterior.

O ambiente capturado pela função não precisa mudar. É o conteúdo da localização associada a `n` que muda.

</details>

Compare com o que tínhamos em `aljabr`: lá, uma closure captura um ambiente imutável. Aqui, a closure pode preservar o acesso a uma localização cujo conteúdo é mutável.

**A diferença não está na existência de closures, mas no que elas podem observar e modificar por meio do ambiente capturado.**

<details>
<summary>Por que não basta dizer que a função interna captura o valor zero de `n`?</summary>

Porque, se a closure capturasse apenas o valor `0`, cada chamada começaria a partir desse mesmo valor e produziria `1`.

O que ela precisa preservar é o acesso à localização associada a `n`. Essa localização continua existindo e seu conteúdo é atualizado a cada chamada. Por isso, as chamadas sucessivas observam os valores `0`, `1`, `2`, `3` etc.

</details>

## 7. Uma decisão de implementação

Até agora, descrevemos o store como uma associação entre localizações e valores. Mas como implementar essa estrutura?

Uma possibilidade é usar um dicionário mutável:

```python
store = {
    localizacao_1: 10,
    localizacao_2: 20,
}
```

Uma atribuição atualiza o dicionário:

```python
store[localizacao_1] = 30
```

Outra possibilidade seria representar o store como uma estrutura imutável: cada atualização produziria uma nova versão, preservando a anterior.

As duas abordagens podem implementar a mesma semântica observável. A diferença está na estratégia usada pelo interpretador para representar e atualizar o store.

<details>
<summary>Se a linguagem oferece mutação, o interpretador também precisa usar estruturas mutáveis em sua implementação?</summary>

Não. A mutação oferecida pela linguagem-objeto é uma característica de sua semântica. A mutação usada na implementação do interpretador é uma escolha de representação.

Um interpretador pode implementar uma linguagem com mutação usando estruturas imutáveis, produzindo uma nova versão do store a cada atualização. Da mesma forma, um interpretador pode usar estruturas mutáveis internamente mesmo quando a linguagem interpretada não oferece essa capacidade ao programador.

</details>

Portanto, não devemos confundir:

- **mutação na linguagem-objeto:** uma construção que permite ao programa modificar valores;
- **mutação na implementação:** uma escolha sobre como o interpretador representa e atualiza suas próprias estruturas.

Um interpretador pode implementar uma linguagem com mutação usando estruturas imutáveis. E, como já vimos na implementação de `letrec`, um interpretador pode usar mutação internamente mesmo quando a linguagem interpretada não oferece essa capacidade ao programador.

## 8. O que ganhamos — e o que muda?

Vamos retomar a pergunta que motivou a aula: por que não conseguíamos implementar nosso contador em `aljabr`?

Agora podemos responder com precisão.

Em `aljabr`, uma chamada a uma função não pode modificar uma informação persistente que será observada por uma chamada posterior. Com o store, passamos a permitir que diferentes avaliações compartilhem localizações e que seus conteúdos sejam modificados.

Isso amplia o que podemos expressar, mas também muda a maneira como devemos pensar sobre a avaliação.

Antes, se uma expressão produzia o valor `v`, poderíamos substituí-la por `v` sem alterar o comportamento do programa. Agora, essa substituição pode ser incorreta se a avaliação da expressão modificar o store ou depender do seu conteúdo.

Por exemplo, avaliar `x` em dois momentos diferentes pode produzir valores diferentes:

```text
var x := 10;

x       // 10

x := 20;

x       // 20
```

O significado de `x` depende do momento em que o consultamos.

<details>
<summary>Se avaliarmos `x` duas vezes, em momentos diferentes, podemos substituir ambas as ocorrências pelo mesmo valor? Por quê?</summary>

Não necessariamente. O valor associado a `x` pode mudar entre as duas avaliações.

No exemplo, a primeira avaliação produz `10`, mas, depois da atribuição, a segunda produz `20`.

Portanto, não podemos tratar toda ocorrência de `x` como se ela representasse um valor fixo independente do momento da avaliação. Seu resultado depende do estado atual do store.

</details>

Essa é uma mudança profunda: **avaliar uma expressão já não é necessariamente apenas calcular um valor; pode também modificar o estado da execução.**

### Para guardar

- O ambiente associa nomes a localizações.
- O store associa localizações a valores.
- Uma declaração cria uma localização e a inicializa.
- Uma atribuição modifica o valor armazenado em uma localização existente.
- Duas variáveis podem compartilhar a mesma localização (*aliasing*).
- Closures podem preservar acesso a localizações mutáveis.
- A avaliação de uma expressão pode depender do store e modificá-lo.

Na próxima aula, vamos explorar outra consequência: se uma avaliação pode modificar o estado, faz sentido avaliar repetidamente uma expressão. Isso nos dará uma motivação concreta para introduzir estruturas de controle como `if` e `while` — e para distinguir expressões de comandos.
