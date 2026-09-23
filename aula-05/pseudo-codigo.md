## Código a partir da BNF

```python
def parse_s_expressao(stream: Stream) -> Ast | Erro:
    """<s-expressão>  ::=  LPAREN OPERADOR <argumentos> RPAREN"""
    expect(stream, LPAREN)
    op = expect(OPERADOR)
    argumentos = parse_argumentos(stream)
    expect(RPAREN)
    return [op, *argumentos]


def parse_argumentos(stream: Stream) -> Ast | Erro:
    """<argumentos>  ::=  <arg> <argumentos> | ε"""
    if peek(RPAREN): 
        return []
    arg = parse_arg(stream)
    argumentos = parse_argumentos(stream)
    return [arg, *argumentos]


def parse_arg(stream: Stream) -> Ast | Erro:
    """<arg>  ::=  INTEIRO | <s-expressão>"""
    if peek(INTEIRO):
        return int(stream.next())
    if peek(LPAREN):
        return parse_s_expressao(stream)
    return Erro("sintaxe: falta s-expressão ou ')'")
```

## Código a partir de uma EBNF

Gramáticas EBNF são uma notação conveniente para escrever analisadores
sintáticos descendentes recursivos. Seus operadores de repetição e opcionalidade
permitem implementar diretamente laços while e condicionais if, evitando
recursão à direita para sequências e reduzindo a profundidade da pilha em
sequências longas. Isso, contudo, não é exclusividade da EBNF: uma BNF
equivalente pode ser otimizada da mesma forma, e recursão continua necessária
para estruturas aninhadas e regras recursivas. Além disso, a EBNF pode ser
usada com outras técnicas de análise, e sua sintaxe varia conforme o dialeto.
Mas o uso da EBNF, de fato, permite perceber mais facilmente a possibilidade de
escrita iterativa da maioria das repetições necessárias, evitando recursões
desnecessárias.

A gramática EBNF para mlisp pode ser dada com uma única regra como a seguir.

Na prática, há diversas variações de EBNFs. Mas alguns operadores são comuns a
todas elas. Por exemplo, o operador `{ X }` especifica que o
elemento `X` (ou qualquer conteúdo entre o `{` e o `}`) é opcional e, se for
usado, pode ser repetido qualquer quantidade de vezes. Outro operador é o `[ X
]` que indica que `X` é opcional (sem repetição). Também há operadores
derivados de expressões regulares como o `*` e o `+` com significado
semelhante; e `( … )` para agrupar símbolos. Naturalmente, os elementos da BNF
clássica são mantidos, tais como terminais, não-terminais, o símbolo de
definição `::=`, a justaposição de elementos e a alternativa com `|`.

Com EBNF, podemos especificar a gramática de mlisp com um único não-terminal (e
uma única regra):

```
<s-expressao> ::= LPAREN OPERADOR { INTEIRO | <s-expressao> } RPAREN
```

A leitura é bastante natural: uma `s-expressao` é definida pela sequência dos
seguintes elementos: um `LPAREN` seguido de um `OPERADOR`; depois disso, **pode
ou não** haver um `INTEIRO` ou uma nova `s-expressão`; e, por fim, deve ser
concluída por um `RPAREN`.

### Implementação de EBNFs

Uma das vantagens de EBNFs é que permite perceber mais claramente as
possibilidades de laços não necessariamente baseados em chamadas a outras
funções. O fato de que tende a reduzir o número de regras e produções também
reduz o total de funções que é necessário implementar. 

Concretamente, a regra acima diz explicitamente para fazer dois `expect`s,
seguidos de um laço do tipo `while`, contendo um expect do `INTEIRO` ou uma
chamada recursiva à própria função; e, por fim, mais um `expect`.

```python
def parse_s_expressao(stream: Stream) -> Ast | Erro:
    """<s-expressao> ::= LPAREN OPERADOR { INTEIRO | <s-expressao> } RPAREN"""

    expect(LPAREN)
    op = expect(OPERADOR)

    args = []
    while not RPAREN(stream.peek()):
        if peek(LPAREN)
            args.append(parse_s_expressao(stream))
        else:
            args.append(expect(INTEIRO))

    expect(RPAREN)
    return [op, *args]
```

A concretização é, mais uma vez, semelhante à que vimos anteriormente. 
