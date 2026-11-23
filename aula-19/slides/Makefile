# Slides em reveal.js a partir de Markdown, via pandoc (>= 3.1).
#
#   make            gera slides.html (4x3)
#   make RATIO=16x9 gera em outra proporção (4x3, 16x9, 16x10, 3x2)
#   make vendor     baixa o reveal.js para ./reveal.js (uso sem internet)
#   make serve      serve a pasta em http://localhost:8000 (notas: tecla S)
#   make clean      remove slides.html
#
# Se existir ./reveal.js, ele é usado; caso contrário, usa-se o CDN.

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

FLAGS := -t revealjs -s \
         --slide-level=2 \
         -V revealjs-url=$(REVEAL_URL) \
         -V width=$(WIDTH) -V height=$(HEIGHT) \
         -V slideNumber="'c/t'" \
         -c style.css \
         --lua-filter=include-code.lua \
         --syntax-definition=algora.xml \
         --syntax-definition=aljabr.xml \
         --highlight-style=pygments

.PHONY: all vendor serve clean FORCE

all: $(OUT)

$(OUT): FORCE $(SRC) style.css include-code.lua $(wildcard exemplos/*)
	$(PANDOC) $(FLAGS) $(SRC) -o $@

vendor:
	git clone --depth 1 --branch $(REVEAL_VER) https://github.com/hakimel/reveal.js.git reveal.js
	rm -rf reveal.js/.git

serve: all
	python3 -m http.server 8000

clean:
	rm -f $(OUT)

FORCE:
