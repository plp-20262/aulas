import pytest
from tipos import Erro, TokenType
from lexer import tokenizador


class TestLexerV4:
    """Testes de aceitação do léxico de `aljabr` v4.

    Estes testes codificam as novas categorias léxicas e palavras reservadas
    introduzidas na versão v4 (conforme README.md, seção 1). Devem falhar até
    que o lexer seja atualizado (Fase 1).
    """

    # --- 1. NOVAS CATEGORIAS LÉXICAS (v4, §1) ---

    @pytest.mark.parametrize("code,expected_type", [
        ("Vazia", TokenType.CONSTR),
        ("Num", TokenType.CONSTR),
        ("Add", TokenType.CONSTR),
        ("Cons", TokenType.CONSTR),
        ("Lista", TokenType.CONSTR),
        ("Expr", TokenType.CONSTR),
        ("Ok", TokenType.CONSTR),
        ("Erro", TokenType.CONSTR),
        ("A1", TokenType.CONSTR),
    ])
    def test_constr_tokens(self, code, expected_type):
        """Construtores/nomes de tipos começam com letra maiúscula."""
        result = tokenizador(code)
        assert not isinstance(result, Erro), f"Erro inesperado para {code!r}: {result}"
        assert len(result) == 1
        assert result[0].type == expected_type
        assert result[0].lexema == code

    @pytest.mark.parametrize("code,expected_type", [
        ("|", TokenType.PIPE),
        ("{", TokenType.LBRACE),
        ("}", TokenType.RBRACE),
    ])
    def test_pipe_and_braces(self, code, expected_type):
        result = tokenizador(code)
        assert not isinstance(result, Erro)
        assert len(result) == 1
        assert result[0].type == expected_type
        assert result[0].lexema == code

    # --- 2. PALAVRAS RESERVADAS v4 ---

    @pytest.mark.parametrize("code,expected_type", [
        ("type", TokenType.TYPE),
        ("match", TokenType.MATCH),
        ("_", TokenType.UNDERSCORE),
    ])
    def test_reserved_words_v4(self, code, expected_type):
        result = tokenizador(code)
        assert not isinstance(result, Erro)
        assert len(result) == 1
        assert result[0].type == expected_type

    # --- 3. '_' NÃO É TRATADO COMO NOME ---

    def test_underscore_not_nome(self):
        """`_` é palavra reservada, não NOME."""
        result = tokenizador("_")
        assert not isinstance(result, Erro)
        assert result[0].type != TokenType.NOME

    # --- 4. CONSTR NÃO É TRATADO COMO NOME ---

    def test_constr_not_nome(self):
        """`Num` é CONSTR, nunca NOME."""
        result = tokenizador("Num")
        assert not isinstance(result, Erro)
        assert result[0].type == TokenType.CONSTR
        assert result[0].type != TokenType.NOME

    # --- 5. NOME MINÚSCULA CONTINUA SENDO NOME ---

    @pytest.mark.parametrize("code", [
        "num", "lista", "x", "meu_nome", "_x", "_",
    ])
    def test_nome_lowercase(self, code):
        """Nomes minúsculos (ou com _) são NOME, exceto `_` reservado."""
        if code == "_":
            # `_` é reservado (testado acima)
            pytest.skip("`_` é palavra reservada v4")
        result = tokenizador(code)
        assert not isinstance(result, Erro)
        assert result[0].type == TokenType.NOME
        assert result[0].lexema == code

    # --- 6. COMBINAÇÃO COM TOKENS EXISTENTES ---

    def test_type_decl_tokens(self):
        """`type Lista = Vazia | Cons(cabeca, cauda)` produz tokens v4."""
        code = "type Lista = Vazia | Cons(cabeca, cauda)"
        result = tokenizador(code)
        assert not isinstance(result, Erro)
        tipos = [t.type for t in result]
        assert TokenType.TYPE in tipos
        assert TokenType.CONSTR in tipos
        assert TokenType.EQUAL in tipos
        assert TokenType.PIPE in tipos
        assert TokenType.LPAREN in tipos
        assert TokenType.RPAREN in tipos

    def test_match_tokens(self):
        """`match e { Vazia => 0 }` produz tokens v4."""
        code = "match e { Vazia => 0 }"
        result = tokenizador(code)
        assert not isinstance(result, Erro)
        tipos = [t.type for t in result]
        assert TokenType.MATCH in tipos
        assert TokenType.LBRACE in tipos
        assert TokenType.RBRACE in tipos
        assert TokenType.CONSTR in tipos
        assert TokenType.ARROW in tipos
        assert TokenType.INTEIRO in tipos
