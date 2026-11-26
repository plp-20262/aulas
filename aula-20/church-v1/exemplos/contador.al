letrec contador =
  fn (v) => 
    if v == 0
    then 0 
    else contador(v - 1)
in
contador(100)
