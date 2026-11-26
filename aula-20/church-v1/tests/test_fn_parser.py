import pytest
from tipos import Erro, TNum
from tests.conftest import token


class TestLambdaParser:
    """Testes de parsing dos lambdas (church v1: parâmetros anotados).

    EBNF (§4.2 do README church):
        exp    ::= ... | fn LPAREN [ params ] RPAREN => exp
        params ::= param { , param }
        param  ::= NOME : tipo

    Forma da AST (questão de projeto da §4.2): lista COM TAG de string,
    no mesmo estilo de ["let", ...]. Operadores binários/unários, em
    contraste, têm um Token na posição 0 — é assim que eval distingue
    os nós sem depender apenas da aridade. Em church, `params` é uma
    lista de pares (nome, tipo).
    """

    # --- 1. FORMA BÁSICA: ["fn", [(nome, tipo), ...], corpo] ---
    @pytest.mark.parametrize("code,expected", [
        ("fn () => 42", ["fn", [], 42]),
        ("fn (x: Num) => x", ["fn", [("x", TNum())], "x"]),
        ("fn (x: Num, y: Num) => x + y",
         ["fn", [("x", TNum()), ("y", TNum())], [token("+"), "x", "y"]]),
        ("fn (x: Num, y: Num, z: Num) => x",
         ["fn", [("x", TNum()), ("y", TNum()), ("z", TNum())], "x"]),
        ("fn (x: Num) => x * x + 1",
         ["fn", [("x", TNum())], [token("+"), [token("*"), "x", "x"], 1]]),
        # espaços são irrelevantes (o lexer os descarta)
        ("fn(x: Num)=>x", ["fn", [("x", TNum())], "x"]),
    ])
    def test_lambda_basic(self, parse, code, expected):
        assert parse(code) == expected

    # --- 2. CORPO (exp) ANINHADO ---
    @pytest.mark.parametrize("code,expected", [
        ("fn (x: Num) => fn (y: Num) => x + y",
         ["fn", [("x", TNum())], ["fn", [("y", TNum())], [token("+"), "x", "y"]]]),
        ("fn () => fn () => 1", ["fn", [], ["fn", [], 1]]),
        ("fn (x: Num) => let y = x in y",
         ["fn", [("x", TNum())], ["let", "y", "x", "y"]]),
        ("fn (x: Num) => x(1)", ["fn", [("x", TNum())], ["app", "x", [1]]]),
        ("fn (f: Num, x: Num) => f(f(x))",
         ["fn", [("f", TNum()), ("x", TNum())], ["app", "f", [["app", "f", ["x"]]]]]),
        ("fn (x: Num) => (x + 1)", ["fn", [("x", TNum())], [token("+"), "x", 1]]),
    ])
    def test_lambda_nested_bodies(self, parse, code, expected):
        assert parse(code) == expected

    # --- 3. LAMBDA EM CONTEXTOS MAIORES ---
    @pytest.mark.parametrize("code,expected", [
        ("let f = fn (x: Num) => x in f",
         ["let", "f", ["fn", [("x", TNum())], "x"], "f"]),
        ("let f = fn (x: Num) => x in f(1)",
         ["let", "f", ["fn", [("x", TNum())], "x"], ["app", "f", [1]]]),
        ("(fn (x: Num) => x)", ["fn", [("x", TNum())], "x"]),
        ("((fn (x: Num) => x))", ["fn", [("x", TNum())], "x"]),
        ("f(fn (x: Num) => x)", ["app", "f", [["fn", [("x", TNum())], "x"]]]),
        ("fn (x: Num) => fn (y: Num) => x",
         ["fn", [("x", TNum())], ["fn", [("y", TNum())], "x"]]),
        ("let f = fn (x: Num) => x * x in f(3)",
         ["let", "f", ["fn", [("x", TNum())], [token("*"), "x", "x"]], ["app", "f", [3]]]),
    ])
    def test_lambda_in_contexts(self, parse, code, expected):
        assert parse(code) == expected


class TestChamadaParser:
    """Testes de parsing da aplicação de funções (inalterado em church).

    EBNF (§2 do README v2):
        chamada ::= atomo { LPAREN [ args ] RPAREN }
        args    ::= exp { , exp }

    Forma da AST: ["app", e_f, [a1, ..., am]]. O agrupamento é à
    esquerda: f(1)(2) = (f(1))(2).
    """

    # --- 1. FORMA BÁSICA: ["app", e_f, [args]] ---
    @pytest.mark.parametrize("code,expected", [
        ("f(1)", ["app", "f", [1]]),
        ("f()", ["app", "f", []]),                       # [ args ] opcional
        ("f(1, 2)", ["app", "f", [1, 2]]),
        ("f (1)", ["app", "f", [1]]),                    # espaço é irrelevante
        ("f(1 + 2, x)", ["app", "f", [[token("+"), 1, 2], "x"]]),
        ("f(g(1))", ["app", "f", [["app", "g", [1]]]]),  # arg é uma chamada
        ("f(1 + 2)", ["app", "f", [[token("+"), 1, 2]]]),
    ])
    def test_application_basic(self, parse, code, expected):
        assert parse(code) == expected

    # --- 2. ASSOCIATIVIDADE À ESQUERDA ---
    @pytest.mark.parametrize("code,expected", [
        ("f(1)(2)", ["app", ["app", "f", [1]], [2]]),
        ("f(1)(2)(3)", ["app", ["app", ["app", "f", [1]], [2]], [3]]),
        ("(fn (x: Num) => x)(1)", ["app", ["fn", [("x", TNum())], "x"], [1]]),
        ("(1 + 2)(3)", ["app", [token("+"), 1, 2], [3]]),
        ("((f))", "f"),
    ])
    def test_application_left_associativity(self, parse, code, expected):
        assert parse(code) == expected

    # --- 3. CHAMADA INTERAGE COM UNÁRIO E PRECEDÊNCIA ---
    @pytest.mark.parametrize("code,expected", [
        ("-f(2)", [token("-"), ["app", "f", [2]]]),
        ("+f(2)", [token("+"), ["app", "f", [2]]]),
        ("f(2) ** 2", [token("**"), ["app", "f", [2]], 2]),
        ("2 ** f(2)", [token("**"), 2, ["app", "f", [2]]]),
        ("f(1) + g(2)", [token("+"), ["app", "f", [1]], ["app", "g", [2]]]),
        ("f(2) * 3", [token("*"), ["app", "f", [2]], 3]),
        ("1 + f(2) * 3", [token("+"), 1, [token("*"), ["app", "f", [2]], 3]]),
        ("let x = f in x(1)", ["let", "x", "f", ["app", "x", [1]]]),
    ])
    def test_application_precedence(self, parse, code, expected):
        assert parse(code) == expected


class TestFnParserErrors:
    """Programas malformados que o parser deve REJEITAR (church v1, §4.2)."""

    @pytest.mark.parametrize("code", [
        "fn x => x",              # '(' ausente após fn
        "fn (x) => x",            # church: parâmetro sem anotação
        "fn (x,) => x",           # vírgula final em params
        "f(1,)",                  # vírgula final em args
        "fn (x) x",               # ':' (e '=>') ausentes
        "1 + fn (x) => x",        # fn não inicia termo/fator/atomo
        "let fn = 1 in fn",       # fn é palavra reservada, não NOME
        "-fn (x) => x",           # fn não inicia chamada/atomo
        "f 1",                    # sem '(' não há aplicação
        "fn () 42",               # '=>' ausente
        "fn (x: Num) =>",         # corpo ausente
        "fn",                     # '(' ausente (EOF)
        "fn (",                   # params/')' ausentes
        "fn (x",                  # ':'/tipo/')' ausentes
        "f(1",                    # ')' ausente em args
        "f(",                     # args/')' ausentes
        "f(,1)",                  # exp ausente após ','
    ])
    def test_rejected_programs(self, parse, code):
        result = parse(code)
        assert isinstance(result, Erro), f"esperava rejeição de {code!r}, obteve {result!r}"

    # --- 2. MENSAGENS DE ERRO ONDE A SPEC FIXA O TERMINAL ESPERADO ---
    def test_missing_paren_after_fn(self, parse):
        result = parse("fn x => x")
        assert isinstance(result, Erro)
        assert "esperava '('" in result.msg

    def test_missing_annotation(self, parse):
        """church v1: parâmetro sem anotação é erro SINTÁTICO (não de tipo)."""
        result = parse("fn (x) => x")
        assert isinstance(result, Erro)
        assert "esperava ':'" in result.msg

    def test_missing_arrow(self, parse):
        result = parse("fn (x: Num) x")
        assert isinstance(result, Erro)
        assert "esperava '=>'" in result.msg

    def test_fn_as_var_name(self, parse):
        result = parse("let fn = 1 in fn")
        assert isinstance(result, Erro)
        assert "esperava nome após 'let'" in result.msg
