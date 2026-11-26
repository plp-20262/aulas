import pytest
from tipos import Erro, Token, TokenType
from lexer import tokenizador


class TestLexerLambda:
    """Testes das novas categorias léxicas de aljabr v2: FN, ARROW e COMMA.

    Ver "§1. Léxico" do README (v2). As três categorias dão suporte a
    lambdas e aplicações: `fn` (palavra reservada), `=>` e `,`.
    """

    # --- 1. ARROW (=>) ---
    # A ordem das regras léxicas importa: ARROW deve vir ANTES de EQUAL,
    # senão `=>` seria tokenizado como `=` seguido de um MISMATCH `>`.
    @pytest.mark.parametrize("code,expected_types", [
        ("=>", [TokenType.ARROW]),
        ("x => y", [TokenType.NOME, TokenType.ARROW, TokenType.NOME]),
        ("a=>b", [TokenType.NOME, TokenType.ARROW, TokenType.NOME]),
        ("fn (x) => x", [
            TokenType.FN, TokenType.LPAREN, TokenType.NOME,
            TokenType.RPAREN, TokenType.ARROW, TokenType.NOME,
        ]),
        ("fn(x)=>x", [
            TokenType.FN, TokenType.LPAREN, TokenType.NOME,
            TokenType.RPAREN, TokenType.ARROW, TokenType.NOME,
        ]),
    ])
    def test_arrow_token(self, code, expected_types):
        result = tokenizador(code)
        assert not isinstance(result, Erro)
        assert [t.type for t in result] == expected_types

    def test_arrow_is_single_token(self):
        """`=>` é UM token ARROW, não `=` + `>` (§1: ordem das regras)."""
        result = tokenizador("=>")
        assert not isinstance(result, Erro)
        assert len(result) == 1
        assert result[0].type == TokenType.ARROW
        assert result[0].lexema == "=>"

    def test_equal_still_works(self):
        """`=` isolado continua sendo EQUAL (usado pelo let)."""
        result = tokenizador("x = 1")
        assert not isinstance(result, Erro)
        assert [t.type for t in result] == [TokenType.NOME, TokenType.EQUAL, TokenType.INTEIRO]

    # --- 1b. `>` não é categoria léxica de aljabr ---
    @pytest.mark.parametrize("code", [">", "= >", "x > y"])
    def test_gt_is_lexical_error(self, code):
        result = tokenizador(code)
        assert isinstance(result, Erro)
        assert "token desconhecido '>'" in result.msg

    # --- 2. COMMA (,) ---
    @pytest.mark.parametrize("code,expected_types", [
        (",", [TokenType.COMMA]),
        ("(x, y)", [TokenType.LPAREN, TokenType.NOME, TokenType.COMMA, TokenType.NOME, TokenType.RPAREN]),
        ("f(1, 2)", [
            TokenType.NOME, TokenType.LPAREN, TokenType.INTEIRO,
            TokenType.COMMA, TokenType.INTEIRO, TokenType.RPAREN,
        ]),
        ("fn () => 1", [
            TokenType.FN, TokenType.LPAREN, TokenType.RPAREN,
            TokenType.ARROW, TokenType.INTEIRO,
        ]),
    ])
    def test_comma_token(self, code, expected_types):
        result = tokenizador(code)
        assert not isinstance(result, Erro)
        assert [t.type for t in result] == expected_types

    # --- 3. FN é palavra reservada ---
    def test_fn_reserved_word(self):
        result = tokenizador("fn")
        assert not isinstance(result, Erro)
        assert len(result) == 1
        assert result[0].type == TokenType.FN
        assert result[0].lexema == "fn"

    # `fn` é prefixo de NOMEs válidos: só é FN quando é o lexema inteiro
    @pytest.mark.parametrize("code", ["fnx", "fn1", "fn_x", "fnx1", "_fn"])
    def test_fn_prefix_is_still_nome(self, code):
        result = tokenizador(code)
        assert not isinstance(result, Erro)
        assert len(result) == 1
        assert result[0].type == TokenType.NOME
        assert result[0].lexema == code

    # Regressão: as palavras reservadas de v1 continuam intactas
    @pytest.mark.parametrize("code,expected_type", [
        ("let", TokenType.LET),
        ("in", TokenType.IN),
    ])
    def test_v1_reserved_words_unchanged(self, code, expected_type):
        result = tokenizador(code)
        assert not isinstance(result, Erro)
        assert len(result) == 1
        assert result[0].type == expected_type

    # Regressão da ordem das regras: `**` não pode virar `*` + `*`
    def test_pow_still_single_token(self):
        result = tokenizador("**")
        assert not isinstance(result, Erro)
        assert len(result) == 1
        assert result[0].type == TokenType.POW

    # --- 4. PROGRAMA COMPLETO ---
    def test_full_lambda_program_tokens(self):
        code = "let quad = fn (x) => x * x in quad(3)"
        result = tokenizador(code)
        assert not isinstance(result, Erro)
        types = [t.type for t in result]
        expected = [
            TokenType.LET, TokenType.NOME, TokenType.EQUAL,
            TokenType.FN, TokenType.LPAREN, TokenType.NOME, TokenType.RPAREN,
            TokenType.ARROW, TokenType.NOME, TokenType.MULT, TokenType.NOME,
            TokenType.IN, TokenType.NOME, TokenType.LPAREN, TokenType.INTEIRO,
            TokenType.RPAREN,
        ]
        assert types == expected
