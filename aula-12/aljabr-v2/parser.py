from tipos import Ast, Erro, monadic_error, Stream, Token
from tipos import INTEIRO, OPS_ADIT, OPS_MULT, POW, LPAREN, RPAREN, TokenType, UNARIO
from tipos import NOME, LET, IN, EQUAL


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
    """exp ::= let NOME = exp in exp | termo { ( + | - ) termo }"""
    if LET(stream.peek()):
        return parse_let(stream)
    
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
    """unario ::= [ + | - ] atomo"""
    if tok := UNARIO(stream.peek()):
        stream.next()
        atomo = parse_atomo(stream)
        return [tok, atomo]
    return parse_atomo(stream)


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
