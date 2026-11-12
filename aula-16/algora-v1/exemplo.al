def criaContador() {
    var n := 0;
    fn () {
      n := n + 1;
      n
    }
}

var c1 := criaContador();
var c2 := criaContador();

c1(); c2();
c1(); c2();
c1();
var n1 := c1();
var n2 := c2();
n1 + n2
