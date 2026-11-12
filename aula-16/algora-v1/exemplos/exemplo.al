def criaContador() {
    var n := 0;

    fn () {
        n := n + 1;
        n
    }
}

var c1 := criaContador();
var c2 := criaContador();

c1();
c1();
c1();
var v1 := c1();

c2();
var v2 := c2();

v1 + v2
