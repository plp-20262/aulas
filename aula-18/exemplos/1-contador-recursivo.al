# Contador recursivo simples em Algora (v2). Problema? Não é um contador
# controlável. Não podemos invocá-lo repetidas vezes para que conte somente
# quando o invocamos. Queremos algo que possamos controlar e que conte e que
# possamos consultar ao fim.
def contador(v) {
    if v == 0 
        { 0 }
    else 
        { contador(v - 1) }
}
contador(100)

# Qual o problema? Usa um estilo funcional puro: sem estado! Mas Algora suporta
# estado e mutação. Como poderíamos resolver o problema, então?
