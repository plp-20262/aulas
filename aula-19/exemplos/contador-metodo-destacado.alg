def Contador() {
    var objeto := {};
    var n := 0;
    objeto.update := fn (valor) { n := valor; n };
    objeto.inc := fn () { n := n + 1; n };
    objeto.dec := fn () { n := n - 1; n };
    objeto.get := fn () { n };
    objeto
}

var c := Contador();
var f := c.inc;        # o método, sem o objeto
f();                   # 1
f();                   # 2
c.get()                # 2
