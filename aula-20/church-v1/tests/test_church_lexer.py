import pytest
from tipos import Erro, TokenType
from lexer import tokenizador


class TestChurchLexer:
    """Novos tokens de church v1 (§4.1)."""

    @pytest.mark.parametrize("code,expected", [
        (":", [(TokenType.COLON, ":")]),
        ("->", [(TokenType.TARROW, "->")]),
        ("Num", [(TokenType.TNUM, "Num")]),
        ("Bool", [(TokenType.TBOOL, "Bool")]),
        ("verdadeiro", [(TokenType.VERDADEIRO, "verdadeiro")]),
        ("falso", [(TokenType.FALSO, "falso")]),
    ])
    def test_new_tokens(self, code, expected):
        result = tokenizador(code)
        assert not isinstance(result, Erro)
        assert [(t.type, t.lexema) for t in result] == expected

    def test_tarrow_before_sub(self):
        """`->` deve casar antes de `-` (senão vira SUB + '>' órfão)."""
        result = tokenizador("(Num) -> Num")
        assert not isinstance(result, Erro)
        assert [t.type for t in result] == [
            TokenType.LPAREN, TokenType.TNUM, TokenType.RPAREN,
            TokenType.TARROW, TokenType.TNUM,
        ]

    def test_type_names_are_whole_lexemes(self):
        """A reserva vale para o lexema INTEIRO: `Numero`/`Foo` são erro léxico."""
        for code in ["Numero", "Booletim", "Foo"]:
            result = tokenizador(code)
            assert isinstance(result, Erro), f"esperava erro léxico em {code!r}"

    def test_boolean_reserved_whole_lexeme(self):
        """`verdadeiro1`/`falsos` são NOMEs válidos (reserva por lexema inteiro)."""
        result = tokenizador("verdadeiro1 falsos")
        assert not isinstance(result, Erro)
        assert all(t.type == TokenType.NOME for t in result)

    def test_spec_tokenization_example(self):
        """Exemplo do §4.1: fn (f: (Num) -> Bool) => f(1)."""
        code = "fn (f: (Num) -> Bool) => f(1)"
        result = tokenizador(code)
        assert not isinstance(result, Erro)
        assert [t.type for t in result] == [
            TokenType.FN, TokenType.LPAREN, TokenType.NOME, TokenType.COLON,
            TokenType.LPAREN, TokenType.TNUM, TokenType.RPAREN,
            TokenType.TARROW, TokenType.TBOOL, TokenType.RPAREN,
            TokenType.ARROW, TokenType.NOME, TokenType.LPAREN,
            TokenType.INTEIRO, TokenType.RPAREN,
        ]
