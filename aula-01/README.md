# RPN

## Notação infixa

Como escrevemos uma expressão matemática na nossa notação
convencional?

```
(b ** 2) - ((4 * a) * c)
```

Essa notação é conhecida como _notação infixa_. Ela é
caracterizada por expressar operações binárias (com dois
operandos) em que o operador é colocado entre os operandos. Por
exemplo, para expressar a soma de 1 e 2, escrevemos `1 + 2`.


## Notação Polonesa (_Polish Notation_)

A notação polonesa também é conhecida como notação de prefixo
(_prefix notation_). Ela difere da notação convencional porque as
expressões colocam o operador antes dos operandos. A soma de 1 e
2, por exemplo, é expressa por `+ 1 2`.

A notação foi inventada por um polonês, motivo pelo qual recebe
esse nome. Mas o aspecto importante é que ela torna desnecessário
o uso de parênteses e até de regras de precedencia para expressar
qualquer operação, ao contrário da notação infixa.

Por exemplo,
compare como devemos expressar o produto de 3 pela soma de 1 e 2.
Em notação infixa, devemos escrever `3 * (1 + 2)`. Os parênteses
são necessários para evitar que garantir a ordem em que as operações devem
ser executadas. Em notação polonesa, podemos escrever `* 3 + 1 2`
Observe que a ordem das operações é dada pela ordem explícita em
que o operadore é observado.

> Observe ainda como a expressão em notação prefix é praticamente
> a própria frase que usamos para especificar: _o produto_ (`*`)
> de 3 pela _soma_ (`+`) de 1 e 2.


## Notação Polonesa Reversa (_Reverse Polish Notation_) 

A notação polonesa reversa inverte a posição do operador que é
colocado depois dos dois operandos. Assim, a soma de 1 e 2, por
exemplo, será expressa por `1 2 +`. Essa notação também é chamada
de notação posfixa ou posfixada. Tal como a notação polonesa
(direta), a notação posfixa permite dispensar o uso de parênteses
da linguagem. 


## Avaliação de expressões RPN

Como avaliar expressões em notação polonesa reversa? Observe que
avaliar tal tipo de expressão é bastante simples. Se iniciarmos
da esquerda para a direita (ordem natural de leitura), basta
encontrar cada operador e aplicá-lo aos operandos imediatamente à
esquerda. Sempre que isso ocorre, podemos simplesmente fazer uma
substituição para chegar em uma expressão mais simples que a
anterior. Se repetimos a operação até que não reste nenhum
operador, chegamos ao valor final da expressão. Veja abaixo como
podemos avaliar a expressão `2 2 3 + 5 * 1 - +`

```
2 2 3 + 5 * 1 - +         -->    (resolvendo 2 3 + pra 5)
2     5 5 * 1 - +         -->    (resolvendo 5 5 * pra 25)
2        25 1 - +         -->    (resolvendo 25 1 - pra 24)
2            24 +         -->    (resolvendo 2 24 + pra 26)
               26
```

A sequência de avaliação acima consiste em produzir uma sequência
de expressões equivalentes, em que vamos repetidamente
substituindo subexpressões por expressões simplificadas, até
chegarmos a uma expressão que não admite mais simplificações.
Quando isso ocorre dizemos que chegamos ao _significado_ da
expressão original (e de todas as anteriores).

## Tabela de rastreamento (_trace table_)

Uma forma alternativa de avaliar as expressões que é mais
apropriada quando queremos criar um interpretador é usar o que
chamamos de _tabela de rastreamento_. Uma tabela de rastreamento
é apenas uma tabela contendo os valores sucessivos de uma
estrutura de dados até que o valor final seja obtido.

> De certa forma, a sequência de avaliação anterior pode ser
> vista como uma tabela de rastreamento. Nela, a estrutura de
> dados usada é algo que possa representar expressões (listas de
> tokens, por exemplo).

Mas RPN é uma das linguagens mais usadas na computação por um
motivo. Ela é facilmente interpretada por uma estrutura de dados
ainda mais simples de manipular: uma pilha. De fato, usaremos
dois valores em nossa tabela: a pilha (que usaremos de memória
para a avaliação da expressão) e uma lista com os tokens ainda
não processados da expressão. A ideia é começar com uma pilha
vazia e todos a expressão original e, passo a passo, consumir os
tokens da expressão, usando a pilha para armazenar valores
pendentes para as operações ainda a processar. Mais uma vez,
vejamos como podemos avaliar a expressão `2 2 3 + 5 * 1 - +`

| Pilha    | Restante da expressão |
|----------|-----------------------|
| []       | [2 2 3 + 5 * 1 - +]   |
| [2]      | [2 3 + 5 * 1 - +]     |
| [2 2]    | [3 + 5 * 1 - +]       |
| [2 2 3]  | [+ 5 * 1 - +]         |
| [2 5]    | [5 * 1 - +]           |
| [2 5 5]  | [* 1 - +]             |
| [2 25]   | [1 - +]               |
| [2 25 1] | [- +]                 |
| [2 24]   | [+]                   |
| [26]     | []                    |


Observe que a cada linha, um token é retirado da lista de tokens
ro restante da expressão (sempre na ordem direta de leitura, da
esquerda pra direita). Se o token for um número, ele é adicionado
ao topo da pilha (que aqui convencionei ser o lado direito). Se o
token for uma operação, dois operandos são retirados do topo da
pilha, a operação correspondente é executada e o valor resultante
é adicionado ao topo da pilha. Observe que isto equivale ao
processo de substituir que fizemos na avaliação anterior (acima).
Em sala de aula, chegamos aos seguinte pseudo-código para essa
operação:

```
se tok é um número
  pilha.push(int(tok))

se tok é operador `+`:
  v1 = int(pilha.pop())
  v2 = int(pilha.pop())
  pilha.push(v1 + v2)
```

## Interpretador

O código do interpretador segue quase que diretamente da lógica
de avaliação acima, baseada na pilha.

> IMPORTANTE: Se você chegou a este ponto da leitura, sugiro que
> tente implementar você mesmo o interpretador, antes de olhar o
> código que fizemos em sala de aula (de fato, fiz alguns ajustes
> para deixar o código mais legível).


## Léxico, Sintaxe e Semântica

A lição importante a se retirar desta aula não é, obviamente, o
aprendizado de RPN em si. O importante é você perceber que
implementamos uma linguagem de programação, com todos os
elementos essenciais do chamado _pipeline_ de processamento: o
analisador léxico (ou _lexer_ ou ainda _tokenizer_), o analisador
sintático (ou _parser_) e o analisador semântico (ou
_interpretador_ propriamente dito). A separação do processamento
nessas três etapas é resultado de anos de experiência acumulada
em LPs. Essa separação independiza processos bastante
independentes, em que cada tem sua própria _responsabilidade_.

Ao _lexer_ compete reconhecer as _palavras_ da linguagem. No
contexto de LPs, contudo, costumamos usar o termo _tokens_ em vez
de _palavras_. É por isso que em algumas implementações podemos
chamar o _lexer_ de _tokenizador_. É responsabilidade do _lexer_
detectar erros de nível _léxico_, tais como _tokens_ ou
caracteres desconhecidos. Uma expressão RPN (na nossa linguagem)
não pode incluir caracteres como letras ou sinais de pontuação.
Encontrar um caractere desses indica que o programador cometeu um
erro léxico e o _lexer_ deve apontar isso.

Ao _parser_ compete reconhecer a formação dos programas. Um
programa bem formado não é uma sequência qualquer de tokens… é
uma sequência de tokens que obedecem a uma ordem apropriada. É
por isso, que a expressão `1 + 2` não é um programa corretamente
escrito em nossa linguagem. Os tokens são claramente pertencentes
à linguagem, mas a ordem em que estão dispostos não é válida para
a sintaxe de RPN. O _parser_ de uma linguagem tem a
responsabilidade de validar a ordem dos tokens de um programa e
de apontar os erros identificados, caso a ordem não seja válida
de acordo com as regras. Observe, contudo, que apenas um programa
válido em nível léxico pode estar correto em nível sintático. Por
isso que se algum erro léxico é identificado, em geral, não faz
sentido iniciar a etapa de processamento sinático.

Por fim, ao _interpretador_ compete _interpretar_ o programa. Ou
seja, aqui estamos falando do nível semântico ou de significado
do programa. Observe que, na prática, _interpretar um programa_ é
sinônimo de _executar um programa_. Naturalmente, observe que só
faz sentido atribuir significado a programas (ou seja, definir
como devem ser executados) se eles estão corretos do ponto de
vista léxico e sintático. Se algum erro tiver sido identificado
nesses níveis anteriores, não é necessário atribuir qualquer
sentido ao programa. Em termos práticos, é admissível que ao
executarmos um programa que foi escrito com erros léxicos e/ou
sintáticos, a interpretação seja abortada, apenas indicando um
erro.

> Observe que a forma como evolui o interpretador separa essas
> três etapas explicitamente em três funções (mas lembre que,
> devido à enorme simplicidade de RPN, nossa versão inicial
> sequer precisava separar as funções tokenizer e parser do
> interpretador). Pra nosso estudo, contudo, é justamente a
> separação do interpretador nessas partes que nos interessa!
