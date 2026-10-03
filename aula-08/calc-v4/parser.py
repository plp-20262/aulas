from tipos import Ast, Erro, monadic_error, Stream, Token
from tipos import INTEIRO, OPS_ADIT, OPS_MULT, POW, LPAREN, RPAREN


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
    """exp ::= termo { ( + | - ) termo }"""
    termo = parse_termo(stream)
    while OPS_ADIT(stream.peek()):
        op = stream.next()           # lê o Token do operador
        termo2 = parse_termo(stream) # lê um novo termo
        termo = [op.lexema, termo, termo2]  # faz folding à esquerda com o lexema

    return termo


@monadic_error
def parse_termo(stream: Stream) -> Ast | Erro:
    """termo ::= fator { ( * | / ) fator }"""
    fator = parse_fator(stream)
    while OPS_MULT(stream.peek()):
        op = stream.next()           # lê o Token do operador
        fator2 = parse_fator(stream) # lê um fator
        fator = [op.lexema, fator, fator2]  # faz o folding à esquerda com o lexema

    return fator


@monadic_error
def parse_fator(stream: Stream) -> Ast | Erro:
    """fator ::= atomo [ ** fator ]"""
    atomo = parse_atomo(stream)  # parte em comum pras duas produções

    if not POW(stream.peek()):  # look-ahead de 1 checando o tipo POW
        return atomo

    stream.next()                # consome o token '**'
    fator = parse_fator(stream)  # chama a função recursivamente (associatividade à direita)
    return ["**", atomo, fator]  # monta o nó da AST


@monadic_error
def parse_atomo(stream: Stream) -> Ast | Erro:
    """atomo ::= INTEIRO | ( exp )"""

    if tok := INTEIRO(stream.peek()):
        stream.next()
        return int(tok.lexema)   # converte o lexema do Token para int

    if LPAREN(stream.peek()):
        stream.next()            # consome '('
        exp = parse_exp(stream)  # recorre à função para exp
        
        if not RPAREN(stream.peek()):
            return Erro("sintaxe: esperava ')'")
            
        stream.next()            # consome ')'
        return exp

    return Erro(f"sintaxe: token inesperado '{stream.peek().lexema if stream.peek() else 'EOF'}'")
