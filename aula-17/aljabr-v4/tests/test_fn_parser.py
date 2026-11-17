import pytest
from tipos import Erro
from tests.conftest import token


class TestLambdaParser:
    """Testes de parsing dos lambdas.

    EBNF (§2 do README v2):
        exp    ::= ... | fn LPAREN [ params ] RPAREN => exp
        params ::= NOME { , NOME }

    Forma da AST (questão de projeto da §4.2): lista COM TAG de string,
    no mesmo estilo de ["let", ...]. Operadores binários/unários, em
    contraste, têm um Token na posição 0 — é assim que eval distingue
    os nós sem depender apenas da aridade.
    """

    # --- 1. FORMA BÁSICA: ["fn", [params], corpo] ---
    @pytest.mark.parametrize("code,expected", [
        ("fn () => 42", ["fn", [], 42]),
        ("fn (x) => x", ["fn", ["x"], "x"]),
        ("fn (x, y) => x + y", ["fn", ["x", "y"], [token("+"), "x", "y"]]),
        ("fn (x, y, z) => x", ["fn", ["x", "y", "z"], "x"]),
        ("fn (x) => x * x + 1", ["fn", ["x"], [token("+"), [token("*"), "x", "x"], 1]]),
        # espaços são irrelevantes (o lexer os descarta)
        ("fn(x)=>x", ["fn", ["x"], "x"]),
    ])
    def test_lambda_basic(self, parse, code, expected):
        assert parse(code) == expected

    # --- 2. CORPO (exp) ANINHADO ---
    @pytest.mark.parametrize("code,expected", [
        # corpo é outro lambda (currying)
        ("fn (x) => fn (y) => x + y",
         ["fn", ["x"], ["fn", ["y"], [token("+"), "x", "y"]]]),
        ("fn () => fn () => 1", ["fn", [], ["fn", [], 1]]),
        # corpo é um let
        ("fn (x) => let y = x in y", ["fn", ["x"], ["let", "y", "x", "y"]]),
        # corpo é uma aplicação
        ("fn (x) => x(1)", ["fn", ["x"], ["app", "x", [1]]]),
        ("fn (f, x) => f(f(x))",
         ["fn", ["f", "x"], ["app", "f", [["app", "f", ["x"]]]]]),
        # corpo é uma expressão aritmética entre parênteses
        ("fn (x) => (x + 1)", ["fn", ["x"], [token("+"), "x", 1]]),
    ])
    def test_lambda_nested_bodies(self, parse, code, expected):
        assert parse(code) == expected

    # --- 3. LAMBDA EM CONTEXTOS MAIORES ---
    @pytest.mark.parametrize("code,expected", [
        ("let f = fn (x) => x in f", ["let", "f", ["fn", ["x"], "x"], "f"]),
        ("let f = fn (x) => x in f(1)",
         ["let", "f", ["fn", ["x"], "x"], ["app", "f", [1]]]),
        # lambda entre parênteses é um atomo (LPAREN exp RPAREN)
        ("(fn (x) => x)", ["fn", ["x"], "x"]),
        ("((fn (x) => x))", ["fn", ["x"], "x"]),
        # lambda como argumento de outra função
        ("f(fn (x) => x)", ["app", "f", [["fn", ["x"], "x"]]]),
        # lambda no corpo de outro lambda
        ("fn (x) => fn (y) => x", ["fn", ["x"], ["fn", ["y"], "x"]]),
        # lambda no corpo de um let que é aplicado
        ("let f = fn (x) => x * x in f(3)",
         ["let", "f", ["fn", ["x"], [token("*"), "x", "x"]], ["app", "f", [3]]]),
    ])
    def test_lambda_in_contexts(self, parse, code, expected):
        assert parse(code) == expected


class TestChamadaParser:
    """Testes de parsing da aplicação de funções.

    EBNF (§2 do README v2):
        chamada ::= atomo { LPAREN [ args ] RPAREN }   ← NOVO
        unario  ::= [ + | - ] chamada                  ← ALTERADO
        args    ::= exp { , exp }

    Forma da AST: ["app", e_f, [a1, ..., am]]. O agrupamento é à
    esquerda: f(1)(2) = (f(1))(2) (§4.2).
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
        ("(fn (x) => x)(1)", ["app", ["fn", ["x"], "x"], [1]]),
        # o atomo ( exp ) também pode ser aplicado (o eval dirá erro)
        ("(1 + 2)(3)", ["app", [token("+"), 1, 2], [3]]),
        ("((f))", "f"),  # parênteses extras apenas agrupam
    ])
    def test_application_left_associativity(self, parse, code, expected):
        assert parse(code) == expected

    # --- 3. CHAMADA INTERAGE COM UNÁRIO E PRECEDÊNCIA ---
    # unario ::= [ + | - ] chamada  ⇒  -f(2) é -(f(2)), não (-f)(2)
    @pytest.mark.parametrize("code,expected", [
        ("-f(2)", [token("-"), ["app", "f", [2]]]),
        ("+f(2)", [token("+"), ["app", "f", [2]]]),
        # fator ::= unario [ ** fator ]  ⇒  a chamada tem a mesma precedência
        # de um atomo dentro da cadeia de operadores
        ("f(2) ** 2", [token("**"), ["app", "f", [2]], 2]),
        ("2 ** f(2)", [token("**"), 2, ["app", "f", [2]]]),
        ("f(1) + g(2)", [token("+"), ["app", "f", [1]], ["app", "g", [2]]]),
        ("f(2) * 3", [token("*"), ["app", "f", [2]], 3]),
        ("1 + f(2) * 3", [token("+"), 1, [token("*"), ["app", "f", [2]], 3]]),
        # chamada após o let, no corpo
        ("let x = f in x(1)", ["let", "x", "f", ["app", "x", [1]]]),
    ])
    def test_application_precedence(self, parse, code, expected):
        assert parse(code) == expected


class TestFnParserErrors:
    """Programas malformados que o parser deve REJEITAR.

    Os 6 primeiros são os da §4.4 do README; os demais cobrem as mesmas
    produções da EBNF com terminals ausentes ou trocados.
    """

    # --- 1. PROGRAMAS DA §4.4 + CASOS ANÁLOGOS ---
    @pytest.mark.parametrize("code", [
        "fn x => x",              # §4.4: '(' ausente após fn
        "fn (x,) => x",           # §4.4: vírgula final em params
        "f(1,)",                  # §4.4: vírgula final em args
        "fn (x) x",               # §4.4: '=>' ausente
        "1 + fn (x) => x",        # §4.4: fn não inicia termo/fator/atomo
        "let fn = 1 in fn",       # §4.4: fn é palavra reservada, não NOME
        "-fn (x) => x",           # fn não inicia chamada/atomo
        "f 1",                    # sem '(' não há aplicação
        "fn () 42",               # '=>' ausente
        "fn (x) =>",              # corpo ausente
        "fn",                     # '(' ausente (EOF)
        "fn (",                   # params/')' ausentes
        "fn (x",                  # ')' ausente
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

    def test_missing_arrow(self, parse):
        result = parse("fn (x) x")
        assert isinstance(result, Erro)
        assert "esperava '=>'" in result.msg

    def test_fn_as_var_name(self, parse):
        """fn é reservada: não pode nomear um let (§1)."""
        result = parse("let fn = 1 in fn")
        assert isinstance(result, Erro)
        assert "esperava nome após 'let'" in result.msg
