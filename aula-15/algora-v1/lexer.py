import re
from tipos import Token, TokenType, Erro

RESERVADAS = {
    "var": TokenType.VAR,
    "def": TokenType.FUNCTION,
    "fn": TokenType.FN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
}

TOKEN_SPEC = [
    ("POW",       r"\*\*"),
    ("ASSIGN",    r":="),       # := antes de =
    ("EQEQ",      r"=="),       # == antes de =
    ("EQUAL",     r"="),
    ("ADD",       r"\+"),
    ("SUB",       r"-"),
    ("MULT",      r"\*"),
    ("DIV",       r"/"),
    ("LPAREN",    r"\("),
    ("RPAREN",    r"\)"),
    ("LBRACE",    r"\{"),
    ("RBRACE",    r"\}"),
    ("SEMICOLON", r";"),
    ("COMMA",     r","),
    ("LT",        r"<"),
    ("INTEIRO",   r"\d+"),
    ("NOME",      r"[a-zA-Z_][a-zA-Z0-9_]*"), # Suporte a letras maiúsculas e minúsculas!
    ("SPACE",     r"[ \t\n\r]+"),
    ("MISMATCH",  r"."),
]

TOKEN_REGEX = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)
)

def tokenizador(programa: str) -> list[Token] | Erro:
    tokens: list[Token] = []
    
    for match in TOKEN_REGEX.finditer(programa):
        kind = match.lastgroup
        value = match.group()
        
        if kind == "SPACE":
            continue
        elif kind == "MISMATCH":
            return Erro(f"erro léxico: token desconhecido '{value}'")
        elif kind == "NOME" and value in RESERVADAS:
            tokens.append(Token(RESERVADAS[value], value))
        else:
            tokens.append(Token(TokenType[kind], value))
            
    return tokens
