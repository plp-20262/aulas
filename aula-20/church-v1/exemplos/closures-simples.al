let id = fn (x) => x in
let multiplicador = fn(fator) => fn (x) => x * fator in

let dobro = multiplicador(2) in
let triplo = id(multiplicador(3)) in


let seis_vezes = fn(x) => dobro(triplo(x)) in
let dezesseis = fn(x) => dobro(dobro(dobro(dobro(x)))) in

dezesseis(2)
