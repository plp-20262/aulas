def criaContador() {
    var n := 0;

    fn () {
        n := n + 1;
        n
    }
}

var contador := criaContador();

contador();
contador();
contador()
