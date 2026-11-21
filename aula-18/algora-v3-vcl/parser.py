from tipos import (
    Ast, Erro, monadic_error, Stream, Token, TokenType,
    Stmt, Expr, VarDecl, Assign, AssignField, FunDecl, ExprStmt, While, Num, Var,
    AnonFun, Call, Record, Field, BinaryOp, UnaryOp, IfExpr, Block,
    INTEIRO, NOME, VAR, FUNCTION, FN, IF, ELSE, WHILE,
    ASSIGN, EQUAL, EQEQ, LT, OPS_ADIT, OPS_MULT, POW,
    UNARIO, LPAREN, RPAREN, LBRACE, RBRACE, SEMICOLON, COMMA, COLON, DOT
)

@monadic_error
def parser(tokens: list[Token]) -> Block | Erro:
    stream = Stream(tokens)
    block = parse_bloco_corpo(stream)
    
    if isinstance(block, Erro):
        return block

    if stream.peek() is not None:
        return Erro(f"sintaxe: tokens não consumidos após fim do programa '{stream.peek().lexema}'")

    return block

@monadic_error
def parse_bloco_corpo(stream: Stream) -> Block | Erro:
    stmts: list[Stmt] = []

    while True:
        tok = stream.peek()

        if VAR(tok) or FUNCTION(tok) or WHILE(tok):
            stmt = parse_comando(stream)
            if isinstance(stmt, Erro): return stmt
            stmts.append(stmt)
            continue

        # qualquer outra coisa é uma expressão (inclui +/-, e erros) ou uma
        # atribuição, que só se distingue de uma expressão depois de lida
        exp = parse_exp_ou_atribuicao(stream)
        if isinstance(exp, Erro): return exp

        if isinstance(exp, Stmt):
            stmts.append(exp)
            continue

        if SEMICOLON(stream.peek()):
            stream.next()
            stmts.append(ExprStmt(exp))
        else:
            return Block(stmts, exp)


@monadic_error
def parse_comando(stream: Stream) -> Stmt | Erro:
    tok = stream.peek()
    if VAR(tok):
        stream.next()
        var_tok = NOME(stream.peek())
        if not var_tok: return Erro("sintaxe: esperava nome após 'var'")
        stream.next()
        
        if not ASSIGN(stream.peek()): return Erro("sintaxe: esperava ':=' em declaração")
        stream.next()
        
        e = parse_exp(stream)
        if isinstance(e, Erro): return e
        
        if not SEMICOLON(stream.peek()): return Erro("sintaxe: esperava ';' após declaração")
        stream.next()
        
        return VarDecl(var_tok.lexema, e)

    if FUNCTION(tok):
        stream.next()
        var_tok = NOME(stream.peek())
        if not var_tok: return Erro("sintaxe: esperava nome de função")
        stream.next()
        
        if not LPAREN(stream.peek()): return Erro("sintaxe: esperava '(' após nome da função")
        stream.next()
        
        params = []
        if not RPAREN(stream.peek()):
            params = parse_params(stream)
            if isinstance(params, Erro): return params
            
        if not RPAREN(stream.peek()): return Erro("sintaxe: esperava ')'")
        stream.next()
        
        body = parse_bloco_delimitado(stream)
        if isinstance(body, Erro): return body
        
        return FunDecl(var_tok.lexema, params, body)

    if WHILE(tok):
        stream.next()
        cond = parse_exp(stream)
        if isinstance(cond, Erro): return cond

        body = parse_bloco_cmd(stream)
        if isinstance(body, Erro): return body

        # while_cmd não é seguido de ';' (como func_decl)
        return While(cond, body)

    return Erro(f"sintaxe: comando inválido '{tok.lexema if tok else 'EOF'}'")

@monadic_error
def parse_bloco_delimitado(stream: Stream) -> Block | Erro:
    if not LBRACE(stream.peek()): return Erro("sintaxe: esperava '{'")
    stream.next()
    
    body = parse_bloco_corpo(stream)
    if isinstance(body, Erro): return body
    
    if not RBRACE(stream.peek()): return Erro("sintaxe: esperava '}' no fim do bloco")
    stream.next()
    return body

@monadic_error
def parse_bloco_cmd(stream: Stream) -> list[Stmt] | Erro:
    """bloco_cmd ::= LBRACE { comando } RBRACE   (corpo do while: sem expressão final)"""
    if not LBRACE(stream.peek()): return Erro("sintaxe: esperava '{' no corpo do 'while'")
    stream.next()

    stmts: list[Stmt] = []
    while not RBRACE(stream.peek()):
        if stream.peek() is None: return Erro("sintaxe: esperava '}' no fim do bloco")
        stmt = parse_item_cmd(stream)
        if isinstance(stmt, Erro): return stmt
        stmts.append(stmt)

    stream.next()   # consome '}'
    return stmts

@monadic_error
def parse_item_cmd(stream: Stream) -> Stmt | Erro:
    """comando ::= func_decl | var_decl ; | atribuicao ; | while_cmd | exp ;"""
    tok = stream.peek()

    if VAR(tok) or FUNCTION(tok) or WHILE(tok):
        return parse_comando(stream)

    # qualquer outra coisa é uma atribuição ou uma expressão seguida de ';'
    exp = parse_exp_ou_atribuicao(stream)
    if isinstance(exp, Erro): return exp
    if isinstance(exp, Stmt): return exp
    if not SEMICOLON(stream.peek()):
        return Erro("sintaxe: esperava ';' após expressão (o corpo do 'while' não tem expressão final)")
    stream.next()
    return ExprStmt(exp)

@monadic_error
def parse_exp_ou_atribuicao(stream: Stream) -> Stmt | Expr | Erro:
    """atribuicao ::= ( NOME | acesso ) := exp ;      |      exp   (sem o ';')

    O alvo de uma atribuição é um `acesso` de tamanho arbitrário, então não há
    lookahead fixo que decida entre `atribuicao` e `exp ;`: lê-se uma `exp` e,
    se o próximo token for ':=', ela precisa ser uma variável ou um acesso a
    campo. Uma exp que termina em ')' (ex.: `(x)`, `(a.b)`) é um grupo entre
    parênteses, que não é alvo válido.
    """
    alvo = parse_exp(stream)
    if isinstance(alvo, Erro): return alvo

    if not ASSIGN(stream.peek()):
        return alvo     # é uma expressão: quem chamou decide sobre o ';'

    if not isinstance(alvo, (Var, Field)) or RPAREN(stream.anterior):
        return Erro("sintaxe: alvo inválido de atribuição")
    stream.next()       # consome ':='

    e = parse_exp(stream)
    if isinstance(e, Erro): return e

    if not SEMICOLON(stream.peek()): return Erro("sintaxe: esperava ';' após atribuição")
    stream.next()

    if isinstance(alvo, Var):
        return Assign(alvo.name, e)
    return AssignField(alvo.obj_expr, alvo.name, e)

@monadic_error
def parse_exp(stream: Stream) -> Expr | Erro:
    tok = stream.peek()
    if IF(tok):
        stream.next()
        cond = parse_exp(stream)
        if isinstance(cond, Erro): return cond
        then_b = parse_bloco_delimitado(stream)
        if isinstance(then_b, Erro): return then_b
        
        if not ELSE(stream.peek()): return Erro("sintaxe: esperava 'else'")
        stream.next()
        
        else_b = parse_bloco_delimitado(stream)
        if isinstance(else_b, Erro): return else_b
        return IfExpr(cond, then_b, else_b)

    if FN(tok):
        stream.next()
        if not LPAREN(stream.peek()): return Erro("sintaxe: esperava '(' após 'fn'")
        stream.next()
        params = []
        if not RPAREN(stream.peek()):
            params = parse_params(stream)
            if isinstance(params, Erro): return params
        if not RPAREN(stream.peek()): return Erro("sintaxe: esperava ')'")
        stream.next()
        
        body = parse_bloco_delimitado(stream)
        if isinstance(body, Erro): return body
        return AnonFun(params, body)

    return parse_comp(stream)

@monadic_error
def parse_comp(stream: Stream) -> Expr | Erro:
    left = parse_soma(stream)
    if isinstance(left, Erro): return left
    
    if EQEQ(stream.peek()) or LT(stream.peek()):
        op = stream.next().lexema
        right = parse_soma(stream)
        if isinstance(right, Erro): return right
        return BinaryOp(op, left, right)
        
    return left

@monadic_error
def parse_soma(stream: Stream) -> Expr | Erro:
    term = parse_termo(stream)
    if isinstance(term, Erro): return term
    while OPS_ADIT(stream.peek()):
        op = stream.next().lexema
        term2 = parse_termo(stream)
        if isinstance(term2, Erro): return term2
        term = BinaryOp(op, term, term2)
    return term

@monadic_error
def parse_termo(stream: Stream) -> Expr | Erro:
    factor = parse_fator(stream)
    if isinstance(factor, Erro): return factor
    while OPS_MULT(stream.peek()):
        op = stream.next().lexema
        factor2 = parse_fator(stream)
        if isinstance(factor2, Erro): return factor2
        factor = BinaryOp(op, factor, factor2)
    return factor

@monadic_error
def parse_fator(stream: Stream) -> Expr | Erro:
    u = parse_unario(stream)
    if isinstance(u, Erro): return u
    if POW(stream.peek()):
        stream.next()
        f = parse_fator(stream)
        if isinstance(f, Erro): return f
        return BinaryOp("**", u, f)
    return u

@monadic_error
def parse_unario(stream: Stream) -> Expr | Erro:
    if UNARIO(stream.peek()):
        op = stream.next().lexema
        operando = parse_posfixo(stream)
        if isinstance(operando, Erro): return operando
        return UnaryOp(op, operando)
    return parse_posfixo(stream)

@monadic_error
def parse_posfixo(stream: Stream) -> Expr | Erro:
    """posfixo ::= atomo { sufixo }      sufixo ::= ( [ args ] ) | . NOME"""
    ast = parse_atomo(stream)
    if isinstance(ast, Erro): return ast

    while LPAREN(stream.peek()) or DOT(stream.peek()):
        if DOT(stream.next()):
            campo = NOME(stream.peek())
            if not campo: return Erro("sintaxe: esperava nome de campo após '.'")
            stream.next()
            ast = Field(ast, campo.lexema)
            continue

        args = []
        if not RPAREN(stream.peek()):
            args = parse_args(stream)
            if isinstance(args, Erro): return args
        if not RPAREN(stream.peek()): return Erro("sintaxe: esperava ')'")
        stream.next()
        ast = Call(ast, args)

    return ast

@monadic_error
def parse_atomo(stream: Stream) -> Expr | Erro:
    tok = stream.peek()
    if INTEIRO(tok):
        stream.next()
        return Num(int(tok.lexema))

    if NOME(tok):
        stream.next()
        return Var(tok.lexema)

    if LBRACE(tok):
        # registro se `{` for seguido de `}` ou de `NOME :`; senão, bloco
        if RBRACE(stream.peek(1)) or (NOME(stream.peek(1)) and COLON(stream.peek(2))):
            return parse_registro(stream)
        return parse_bloco_delimitado(stream)

    if LPAREN(tok):
        stream.next()
        e = parse_exp(stream)
        if isinstance(e, Erro): return e
        if not RPAREN(stream.peek()): return Erro("sintaxe: esperava ')'")
        stream.next()
        return e

    return Erro(f"sintaxe: token inesperado '{tok.lexema if tok else 'EOF'}'")

@monadic_error
def parse_registro(stream: Stream) -> Record | Erro:
    """registro ::= LBRACE [ campo { COMMA campo } ] RBRACE      campo ::= NOME : exp"""
    stream.next()   # consome '{'
    campos: list[tuple[str, Expr]] = []

    if not RBRACE(stream.peek()):
        while True:
            nome = NOME(stream.peek())
            if not nome: return Erro("sintaxe: esperava nome de campo")
            stream.next()
            if any(nome.lexema == n for n, _ in campos):
                return Erro(f"sintaxe: campo '{nome.lexema}' repetido no registro")

            if not COLON(stream.peek()): return Erro("sintaxe: esperava ':' após nome de campo")
            stream.next()

            e = parse_exp(stream)
            if isinstance(e, Erro): return e
            campos.append((nome.lexema, e))

            if not COMMA(stream.peek()): break
            stream.next()

    if not RBRACE(stream.peek()): return Erro("sintaxe: esperava '}' no fim do registro")
    stream.next()
    return Record(campos)

def parse_params(stream: Stream) -> list[str] | Erro:
    tok = NOME(stream.peek())
    if not tok: return Erro("sintaxe: esperava parâmetro")
    stream.next()
    params = [tok.lexema]
    while COMMA(stream.peek()):
        stream.next()
        tok = NOME(stream.peek())
        if not tok: return Erro("sintaxe: esperava nome após ','")
        stream.next()
        params.append(tok.lexema)
    return params

def parse_args(stream: Stream) -> list[Expr] | Erro:
    first = parse_exp(stream)
    if isinstance(first, Erro): return first
    args = [first]
    while COMMA(stream.peek()):
        stream.next()
        e = parse_exp(stream)
        if isinstance(e, Erro): return e
        args.append(e)
    return args
