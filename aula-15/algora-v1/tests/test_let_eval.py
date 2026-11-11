from algora import executar_programa

def test_eval_var_declaracao():
    prog = """
    var x := 10;
    var y := 20;
    x + y
    """
    assert executar_programa(prog) == 30

def test_eval_atribuicao_mutavel():
    prog = """
    var contador := 0;
    contador := contador + 1;
    contador := contador + 5;
    contador
    """
    assert executar_programa(prog) == 6

def test_eval_escopo_de_bloco_var():
    prog = """
    var x := 100;
    {
        var x := 5;
        x
    };
    x
    """
    assert executar_programa(prog) == 100
