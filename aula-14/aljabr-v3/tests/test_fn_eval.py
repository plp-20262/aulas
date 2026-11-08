import pytest
from tipos import Erro
from aljabr import Closure
from tests.conftest import assert_error, run, token


class TestSpecPrograms:
    """Tabela de programas da §4.4 do README (v2) — ponta-a-ponta.

    Cada programa passa por lexer, parser e eval (helper `run`).
    """

    # --- 1. PROGRAMAS QUE DEVOLVEM VALOR ---
    @pytest.mark.parametrize("code,expected", [
        ("let quad = fn (x) => x * x in quad(3) + quad(5)", 34),
        ("(fn (x, y) => x + y)(2, 3)", 5),
        ("(fn () => 42)()", 42),
        ("(fn (x) => fn (y) => x + y)(2)(3)", 5),
        ("let n = 7 in let soma_n = fn (x) => x + n in let n = 100 in soma_n(3)", 10),
        ("let f = fn (x) => x in -f(2)", -2),
        ("let f = fn (x) => x in f(2) ** 2", 4),
        # §3: corpo nunca é avaliado na criação do closure
        ("let f = fn (x) => x + y in 10", 10),
    ])
    def test_spec_programs_return_values(self, code, expected):
        assert run(code) == expected

    # --- 2. PROGRAMAS QUE DEVOLVEM erro ---
    # (msg_substring=None ⇒ basta ser Erro; a spec só fixa o resultado)
    @pytest.mark.parametrize("code,msg_substring", [
        ("let f = fn (x, y) => x + y in f(1)", "aridade"),       # (AppAridade)
        ("5(3)", "não-função"),                                  # (AppNaoFuncao)
        ("let q = fn (x) => x in q + 1", None),                  # lift vê closure
        ("let f = fn (x) => x + y in f(1)", None),               # ρ lifted: y ∉ dom(ρ0)
        ("let x = 1/0 in 5", "divisão por zero"),                # erro é estrito
        ("(fn (x) => 5)(1/0)", "divisão por zero"),              # erro no argumento
    ])
    def test_spec_programs_return_errors(self, code, msg_substring):
        assert_error(run(code), msg_substring)


class TestLambdaEval:
    """Regra (Lam) (§3): o lambda avalia para closure que captura ρ,
    sem avaliar o corpo."""

    def test_lambda_evaluates_to_closure(self, eval_ast, env):
        result = eval_ast(["fn", ["x"], "x"], env)
        assert isinstance(result, Closure)
        assert not isinstance(result, Erro)

    def test_body_not_evaluated_at_creation(self, eval_ast, env):
        """(Lam) não tem premissas: 1/0 no corpo nunca executa."""
        result = eval_ast(["fn", ["x"], [token("/"), "x", 0]], env)
        assert isinstance(result, Closure)

    def test_closure_captures_creation_env(self, eval_ast):
        """ρ0 capturada no momento da criação vence o ambiente de chamada."""
        f = eval_ast(["fn", ["x"], [token("+"), "x", "y"]], {"y": 10})
        assert eval_ast(["app", "f", [5]], {"f": f, "y": 99}) == 15

    def test_application_does_not_mutate_envs(self, eval_ast):
        """ρ0 e ρ não são modificadas: aplicações repetidas são independentes."""
        f = eval_ast(["fn", ["x"], [token("+"), "x", "n"]], {"n": 10})
        call_env = {"f": f, "n": 100}
        assert eval_ast(["app", "f", [1]], call_env) == 11
        assert eval_ast(["app", "f", [2]], call_env) == 12
        assert call_env == {"f": f, "n": 100}  # ρ de chamada intacta

    def test_var_bound_to_closure(self, eval_ast):
        """(Var) devolve o que ρ(x) guarda — closures incluídas."""
        f = eval_ast(["fn", ["x"], "x"], {})
        assert eval_ast("f", {"f": f}) is f


class TestAppEval:
    """Regras (App), (AppNaoFuncao) e (AppAridade) (§3)."""

    # --- 1. (App) CASOS FELIZES ---
    @pytest.mark.parametrize("lam,args,expected", [
        (["fn", ["x"], [token("*"), "x", 2]], [21], 42),
        (["fn", [], 42], [], 42),
        (["fn", ["x", "y"], [token("+"), "x", "y"]], [2, 3], 5),
        (["fn", ["x"], ["let", "y", [token("+"), "x", 1], [token("*"), "y", 2]]], [4], 10),
    ])
    def test_application(self, eval_ast, env, lam, args, expected):
        assert eval_ast(["app", lam, args], env) == expected

    def test_arguments_evaluated_in_call_env(self, eval_ast):
        """⟨a_i, ρ⟩ ⇓ v_i: argumentos no ambiente DE CHAMADA, não no closure."""
        assert eval_ast(["app", ["fn", ["x"], "x"], [[token("+"), "a", 1]]], {"a": 41}) == 42

    def test_param_shadows_closure_env(self, eval_ast):
        """ρ0[p ↦ v]: o parâmetro sombreia o que ρ0 tinha para o mesmo nome."""
        f = eval_ast(["fn", ["x"], "x"], {"x": 1})
        assert eval_ast(["app", "f", [9]], {"f": f, "x": 0}) == 9

    # --- 2. (AppNaoFuncao): v_f ∉ Clo ---
    @pytest.mark.parametrize("lam", [
        5,                        # 5(3)
        [token("+"), 1, 2],       # (1 + 2)(3)
    ])
    def test_app_not_function(self, eval_ast, env, lam):
        assert_error(eval_ast(["app", lam, [3]], env), "não-função")

    def test_app_not_function_variable(self, eval_ast):
        """Variável não-função: ⟨x,ρ⟩⇓5 ∉ Clo ⇒ erro."""
        assert_error(eval_ast(["app", "x", [1]], {"x": 5}), "não-função")

    # --- 3. (AppAridade): m ≠ n ---
    @pytest.mark.parametrize("lam,args", [
        (["fn", ["x"], "x"], []),        # menos argumentos
        (["fn", ["x"], "x"], [1, 2]),    # mais argumentos
        (["fn", [], 42], [1]),           # zero parâmetros, um argumento
    ])
    def test_app_arity_error(self, eval_ast, env, lam, args):
        assert_error(eval_ast(["app", lam, args], env), "aridade")

    def test_arity_checked_before_arguments(self, eval_ast, env):
        """§3 (escolha de projeto): a aridade é verificada ANTES de avaliar
        os argumentos — o argumento com 1/0 nem chega a ser avaliado."""
        result = eval_ast(["app", ["fn", ["x", "y"], "x"], [[token("/"), 1, 0]]], env)
        assert_error(result, "aridade")
        assert "divisão por zero" not in result.msg

    # --- 4. PROPAGAÇÃO DE erro (convenção da §3) ---
    def test_error_in_argument_propagates(self, eval_ast, env):
        result = eval_ast(["app", ["fn", ["x"], "x"], [[token("/"), 1, 0]]], env)
        assert_error(result, "divisão por zero")

    def test_error_in_body_propagates(self, eval_ast, env):
        result = eval_ast(["app", ["fn", ["x"], [token("/"), "x", 0]], [1]], env)
        assert_error(result, "divisão por zero")

    def test_error_in_function_expression_propagates(self, eval_ast, env):
        """⟨e_f, ρ⟩ ⇓ erro ⇒ a premissa (App) não se aplica: resultado erro."""
        result = eval_ast(["app", [token("/"), 1, 0], [1]], env)
        assert_error(result, "divisão por zero")

    def test_unbound_var_in_body(self, eval_ast, env):
        """Ambiente lifted: ρ0(y) = erro para y ∉ dom(ρ0)."""
        result = eval_ast(["app", ["fn", ["x"], [token("+"), "x", "y"]], [1]], env)
        assert_error(result, "variável 'y' não vinculada")


class TestLexicalScope:
    """Escopo léxico: o corpo é avaliado em ρ0, o ambiente de CRIAÇÃO
    (regra (App) da §3). O Bloco 7.1 contrasta com (AppDin), em que o
    corpo seria avaliado em ρ — aljabr usa escopo léxico."""

    @pytest.mark.parametrize("code,expected", [
        # Bloco 7.1: com escopo dinâmico valeria 25; com léxico, 15
        ("let a = 10 in let f = fn (x) => x + a in let a = 20 in f(5)", 15),
        # parâmetro sombreia o let externo, sem efeito colateral
        ("let x = 1 in (fn (x) => x)(9)", 9),
        ("let x = 1 in let r = (fn (x) => x)(9) in x + r", 10),
        # closure devolvida por closure: ρ0 estendida com p ↦ v vira ρ0' interna
        ("let f = fn () => fn (x) => x in f()(7)", 7),
        ("let g = fn (x) => fn (y) => x + y in g(10)(5)", 15),
        # closures são valores de primeira classe: podem ser argumentos
        ("let inc = fn (x) => x + 1 in (fn (f, x) => f(f(x)))(inc, 1)", 3),
        # aplicação parcial via aninhamento (currying) reutiliza a closure
        ("let dobra = fn (x) => fn (y) => x * y in let d5 = dobra(5) in d5(2) + d5(3)", 25),
    ])
    def test_lexical_scoping(self, code, expected):
        assert run(code) == expected


class TestLiftWithClosures:
    """§3: Val agora inclui closures, então o "caso contrário" do lift
    também cobre operações aritméticas sobre funções — nenhuma regra
    nova é necessária, o lift que já tínhamos produz erro."""

    @pytest.mark.parametrize("code", [
        "q + 1",
        "1 + q",
        "q * q",
        "q - 1",
        "q / 2",
        "q ** 2",
        "2 ** q",
        "-q",
        "+q",
    ])
    def test_arithmetic_on_closure_is_error(self, code):
        result = run(f"let q = fn (x) => x in {code}")
        assert isinstance(result, Erro), f"esperava erro em {code!r}, obteve {result!r}"

    def test_lift_propagates_error_before_touching_closure(self, eval_ast, env):
        """O lift ainda propaga erros monadicamente antes de aplicar f_op."""
        result = eval_ast([token("+"), [token("/"), 1, 0], "q"],
                          {**env, "q": eval_ast(["fn", ["x"], "x"], env)})
        assert_error(result, "divisão por zero")
