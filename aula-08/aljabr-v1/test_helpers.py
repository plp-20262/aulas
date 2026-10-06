from lexer import tokenizador
from tipos import Erro, Token

def token(lexema: str) -> Token:
    """Create a Token from a lexeme string using the lexer. Test utility."""
    tokens = tokenizador(lexema)
    if isinstance(tokens, Erro) or len(tokens) != 1:
        raise ValueError(f"invalid single lexeme: {lexema!r}")
    return tokens[0]