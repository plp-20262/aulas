from tipos import Ast, Erro, monadic_error, Stream, Token
from tipos import INTEIRO, OPS_ADIT, OPS_MULT, POW, LPAREN, RPAREN, TokenType, UNARIO
from tipos import NOME, LET, IN, EQUAL, FN, ARROW, COMMA


@monadic_error
def parser(tokens: list[Token]) -> Ast | Erro:
    stream = Stream(tokens)
    erro = ast = parse_exp(stream)

    if isinstance(erro, Erro):
        return erro

    # se ainda há tokens no stream, é erro
    if stream.peek() is not None:
        return Erro("sintaxe: tokens depois da expressão")

    return ast


@monadic_error
def parse_exp(stream: Stream) -> Ast | Erro:
    """exp ::= let NOME = exp in exp
             | fn LPAREN [ params ] RPAREN => exp          (v2, §2)
             | termo { ( + | - ) termo }"""
    if LET(stream.peek()):
        return parse_let(stream)

    # v2 (§4.2): se o próximo token é FN, a alternativa `fn` de exp decide
    # a derivação (a gramática continua LL(1): FN não inicia nenhuma outra
    # produção alcançável daqui)
    if FN(stream.peek()):
        return parse_lambda(stream)

    termo = parse_termo(stream)
    while OPS_ADIT(stream.peek()):
        op = stream.next()           # lê o Token do operador
        termo2 = parse_termo(stream) # lê um novo termo
        termo = [op, termo, termo2]  # faz folding à esquerda com o Token

    return termo


@monadic_error
def parse_let(stream: Stream) -> Ast | Erro:
    """let ::= let NOME = exp in exp"""
    stream.next()  # consome LET
    
    var_tok = NOME(stream.peek())
    if not var_tok:
        return Erro("sintaxe: esperava nome após 'let'")
    stream.next()  # consome NOME
    var = var_tok.lexema
    
    if not EQUAL(stream.peek()):
        return Erro("sintaxe: esperava '=' após nome")
    stream.next()  # consome '='
    
    e1 = parse_exp(stream)
    if isinstance(e1, Erro):
        return e1
    
    if not IN(stream.peek()):
        return Erro("sintaxe: esperava 'in' após expressão de vinculação")
    stream.next()  # consome IN
    
    e2 = parse_exp(stream)
    if isinstance(e2, Erro):
        return e2
    
    return ["let", var, e1, e2]


@monadic_error
def parse_lambda(stream: Stream) -> Ast | Erro:
    """fn LPAREN [ params ] RPAREN => exp          (alternativa `fn` de exp, §2)

    Derivação mecânica da EBNF (§4.2):
        terminal T       → expect(T)  (aqui: checagem explícita + stream.next)
        [ X ]            → if o próximo token pode iniciar X
        não-terminal X   → chamada à função correspondente

    A AST resultante é a lista COM TAG ["fn", [params], corpo] — a tag de
    string distingue o nó dos operadores binários/unários, cujo elemento
    [0] é um Token (questão de projeto da §4.2).
    """
    stream.next()  # consome FN

    if not LPAREN(stream.peek()):
        return Erro("sintaxe: esperava '(' após 'fn'")
    stream.next()  # consome '('

    params: list[str] = []
    if not RPAREN(stream.peek()):     # [ params ] vira if
        params = parse_params(stream)
        if isinstance(params, Erro):
            return params

    if not RPAREN(stream.peek()):
        return Erro("sintaxe: esperava ')' após parâmetros")
    stream.next()  # consome ')'

    if not ARROW(stream.peek()):
        return Erro("sintaxe: esperava '=>' após parâmetros")
    stream.next()  # consome '=>'

    corpo = parse_exp(stream)
    if isinstance(corpo, Erro):
        return corpo

    return ["fn", params, corpo]


@monadic_error
def parse_params(stream: Stream) -> list[str] | Erro:
    """params ::= NOME { , NOME }                  (§2)

    Chamado apenas quando há ao menos um NOME (o `[ ]` de `[ params ]`
    é decidido pelo chamador, em parse_lambda).
    """
    tok = NOME(stream.peek())
    if not tok:
        return Erro("sintaxe: esperava nome de parâmetro")
    stream.next()  # consome NOME
    params = [tok.lexema]

    while COMMA(stream.peek()):       # { , NOME } vira while
        stream.next()  # consome ','
        tok = NOME(stream.peek())
        if not tok:
            return Erro("sintaxe: esperava nome após ','")
        stream.next()  # consome NOME
        params.append(tok.lexema)

    return params


@monadic_error
def parse_args(stream: Stream) -> list[Ast] | Erro:
    """args ::= exp { , exp }                        (§2)

    Chamado apenas quando o próximo token não é RPAREN (o `[ ]` de
    `[ args ]` é decidido pelo chamador, em parse_chamada).
    """
    primeira = parse_exp(stream)
    if isinstance(primeira, Erro):
        return primeira
    args = [primeira]

    while COMMA(stream.peek()):       # { , exp } vira while
        stream.next()  # consome ','
        e = parse_exp(stream)
        if isinstance(e, Erro):
            return e
        args.append(e)

    return args


@monadic_error
def parse_termo(stream: Stream) -> Ast | Erro:
    """termo ::= fator { ( * | / ) fator }"""
    fator = parse_fator(stream)
    while OPS_MULT(stream.peek()):
        op = stream.next()           # lê o Token do operador
        fator2 = parse_fator(stream) # lê um fator
        fator = [op, fator, fator2]  # faz o folding à esquerda com o Token

    return fator


@monadic_error
def parse_unario(stream: Stream) -> Ast | Erro:
    """unario ::= [ + | - ] chamada                  (§2: ALTERADO em v2)"""
    if tok := UNARIO(stream.peek()):
        stream.next()
        chamada = parse_chamada(stream)
        return [tok, chamada]
    return parse_chamada(stream)


@monadic_error
def parse_chamada(stream: Stream) -> Ast | Erro:
    """chamada ::= atomo { LPAREN [ args ] RPAREN }  (§2: NOVO em v2)

    Derivação mecânica da EBNF (§4.2):
        { X }            → while o próximo token pode iniciar X
        [ X ]            → if o próximo token pode iniciar X
        terminal T       → expect(T)

    O agrupamento é à esquerda: f(1)(2) = (f(1))(2), porque cada LPAREN
    encontrado reescreve o ast acumulado em ["app", ast, args].
    """
    ast = parse_atomo(stream)
    if isinstance(ast, Erro):
        return ast

    while LPAREN(stream.peek()):      # { ... } vira while
        stream.next()                 # consome '('
        args: list[Ast] = []
        if not RPAREN(stream.peek()): # [ ... ] vira if
            args = parse_args(stream)
            if isinstance(args, Erro):
                return args
        if not RPAREN(stream.peek()):
            return Erro("sintaxe: esperava ')'")
        stream.next()                 # consome ')'
        ast = ["app", ast, args]      # agrupamento à esquerda

    return ast


@monadic_error
def parse_fator(stream: Stream) -> Ast | Erro:
    """fator ::= unario [ ** fator ]"""
    unario = parse_unario(stream)

    if not POW(stream.peek()):
        return unario

    op = stream.next()
    fator = parse_fator(stream)
    return [op, unario, fator]


@monadic_error
def parse_atomo(stream: Stream) -> Ast | Erro:
    """atomo ::= INTEIRO | NOME | let NOME = exp in exp | ( exp )"""

    if tok := INTEIRO(stream.peek()):
        stream.next()
        return int(tok.lexema)   # converte o lexema do Token para int

    if tok := NOME(stream.peek()):
        stream.next()
        return tok.lexema   # retorna o nome da variável como string

    if LET(stream.peek()):
        return parse_let(stream)

    if LPAREN(stream.peek()):
        stream.next()            # consome '('
        exp = parse_exp(stream)  # recorre à função para exp
        
        if not RPAREN(stream.peek()):
            return Erro("sintaxe: esperava ')'")
            
        stream.next()            # consome ')'
        return exp

    return Erro(f"sintaxe: token inesperado '{stream.peek().lexema if stream.peek() else 'EOF'}'")
