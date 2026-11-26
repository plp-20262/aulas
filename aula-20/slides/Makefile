# Slides em reveal.js a partir de Markdown, via pandoc (>= 3.1).
#
#   make            gera slides.html (4x3)
#   make RATIO=16x9 gera em outra proporção (4x3, 16x9, 16x10, 3x2)
#   make vendor     baixa o reveal.js para ./reveal.js (uso sem internet)
#   make serve      serve a pasta em http://localhost:8000 (notas: tecla S)
#   make watch      regera slides.html a cada gravação (sem dependências)
#   make live       watch + servidor com recarga automática do navegador (precisa de npx)
#   make clean      remove slides.html
#
# Se existir ./reveal.js, ele é usado; caso contrário, usa-se o CDN.

SHELL := /bin/bash

PANDOC     ?= pandoc
SRC        := slides.md
OUT        := slides.html
REVEAL_VER := 5.1.0

# Proporção do slide: make RATIO=4x3 (padrão), 16x9, 16x10 ou 3x2.
# A largura de referência é sempre 1280; só a altura muda, então
# fontes e espaçamentos ficam iguais em qualquer proporção.
RATIO  ?= 4x3
WIDTH  := 1280
HEIGHT_4x3   := 960
HEIGHT_16x9  := 720
HEIGHT_16x10 := 800
HEIGHT_3x2   := 853
HEIGHT := $(strip $(or $(HEIGHT_$(RATIO)),$(error RATIO desconhecido: $(RATIO))))
REVEAL_URL := $(if $(wildcard reveal.js/dist/reveal.js),reveal.js,https://cdn.jsdelivr.net/npm/reveal.js@$(REVEAL_VER))

LIVE_FLAGS := $(if $(LIVE),-V hash=false --include-after-body=<(printf '%s' '<script>addEventListener("DOMContentLoaded",()=>{const go=()=>{const secs=[...document.querySelectorAll(".reveal .slides section")].filter(s=>!s.querySelector("section"));const cur=secs.map(s=>s.textContent.replace(/\s+/g," ")+"|"+s.querySelectorAll("*").length);const prev=JSON.parse(sessionStorage.getItem("r-secs")||"[]");sessionStorage.setItem("r-secs",JSON.stringify(cur));let target=cur.findIndex((v,i)=>v!==prev[i]);if(target<0)target=Number(sessionStorage.getItem("r-idx")||0);const indices=Reveal.getIndices(secs[target]);if(indices)Reveal.slide(indices.h,indices.v,0);Reveal.on("slidechanged",()=>{const i=secs.indexOf(Reveal.getCurrentSlide());if(i>=0)sessionStorage.setItem("r-idx",i)})};Reveal.isReady()?go():Reveal.on("ready",go)});</script>'),)

FLAGS := -t revealjs -s \
         --slide-level=2 \
         -V revealjs-url=$(REVEAL_URL) \
         -V width=$(WIDTH) -V height=$(HEIGHT) \
         -V slideNumber="'c/t'" \
         -c style.css \
         --lua-filter=include-code.lua \
         --syntax-definition=algora.xml \
         --syntax-definition=aljabr.xml \
         --highlight-style=pygments \
         $(LIVE_FLAGS)

.PHONY: all vendor serve watch live clean FORCE

all: $(OUT)

$(OUT): FORCE $(SRC) style.css include-code.lua $(wildcard exemplos/*)
	$(PANDOC) $(FLAGS) $(SRC) -o $@

vendor:
	git clone --depth 1 --branch $(REVEAL_VER) https://github.com/hakimel/reveal.js.git reveal.js
	rm -rf reveal.js/.git

serve: all
	python3 -m http.server 8000

# Regera ao detectar mudança em qualquer fonte (consulta a cada 1 s).
watch:
	@echo "Observando $(SRC), style.css, include-code.lua, exemplos/ (Ctrl-C para sair)"
	@last=""; while true; do \
	  cur=$$(cat $(SRC) style.css include-code.lua exemplos/* 2>/dev/null | cksum); \
	  if [ "$$cur" != "$$last" ]; then last="$$cur"; $(MAKE) --no-print-directory all && echo "[$$(date +%H:%M:%S)] slides.html atualizado"; fi; \
	  sleep 1; done

# watch + servidor que recarrega o navegador quando slides.html muda.
live:
	@trap 'kill 0' EXIT; $(MAKE) --no-print-directory watch LIVE=1 & \
	npx --yes live-server --port=8000 --open=/slides.html --watch=slides.html --no-css-inject

clean:
	rm -f $(OUT)

FORCE:
