-- Filtro Lua do pandoc: carrega o conteúdo de blocos de código a partir de
-- arquivos externos, para manter os slides sincronizados com `exemplos/`.
--
-- Uso em slides.md:
--
--   ```{.text include="exemplos/animais-oo.alg"}
--   ```
--
--   ```{.text include="exemplos/animais-oo.alg" from=3 to=12}
--   ```
--
-- (`from` e `to` são opcionais: intervalo de linhas, inclusive.)
-- Se o arquivo não existir, o build não falha: o bloco mostra um aviso.

function CodeBlock(cb)
  local path = cb.attributes["include"]
  if not path then return nil end

  local f = io.open(path, "r")
  if not f then
    io.stderr:write("[include-code] arquivo não encontrado: " .. path .. "\n")
    cb.text = "-- arquivo não encontrado: " .. path
    cb.attributes["include"] = nil
    return cb
  end

  local lines = {}
  for line in f:lines() do lines[#lines + 1] = line end
  f:close()

  local from = tonumber(cb.attributes["from"]) or 1
  local to = math.min(tonumber(cb.attributes["to"]) or #lines, #lines)

  cb.text = table.concat(lines, "\n", from, to)
  cb.attributes["include"] = nil
  cb.attributes["from"] = nil
  cb.attributes["to"] = nil
  return cb
end
