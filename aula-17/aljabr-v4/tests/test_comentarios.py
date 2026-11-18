import pytest
from aljabr import remover_comentarios


class TestComentarios:
    """Testes de aceitação de comentários com `#` (aljabr v4).

    Estes testes codificam o comportamento esperado: todo conteúdo de uma
    linha a partir do primeiro `#` é ignorado. Devem falhar até que a função
    `remover_comentarios` seja implementada em `aljabr.py` (Fase 1).
    """

    # --- 1. COMENTÁRIO EM LINHA INTEIRA ---

    def test_comentario_linha_inteira(self):
        """Linha iniciada com # é ignorada completamente."""
        fonte = "# isso é um comentário\n42"
        assert remover_comentarios(fonte) == "\n42"

    def test_varias_linhas_de_comentario(self):
        """Múltiplas linhas de comentário seguidas são todas ignoradas."""
        fonte = "# comentário 1\n# comentário 2\n# comentário 3\n7"
        assert remover_comentarios(fonte) == "\n\n\n7"

    # --- 2. COMENTÁRIO INLINE (CÓDIGO ANTES DO #) ---

    def test_comentario_inline(self):
        """Código antes do # é preservado; comentário depois é removido."""
        fonte = "let x = 1 # atribui 1\nin x"
        assert remover_comentarios(fonte) == "let x = 1 \nin x"

    def test_comentario_inline_sem_espaco(self):
        """# pode aparecer logo após o código, sem espaço."""
        fonte = "1+2#soma\ny"
        assert remover_comentarios(fonte) == "1+2\ny"

    # --- 3. MÚLTIPLOS # NA MESMA LINHA ---

    def test_varios_hashes_mesma_linha(self):
        """O primeiro # inicia o comentário; os demais fazem parte dele."""
        fonte = "42 # primeiro # segundo"
        assert remover_comentarios(fonte) == "42 "

    # --- 4. COMENTÁRIO NO FINAL DO ARQUIVO ---

    def test_comentario_final_sem_quebra_de_linha(self):
        """# no final do arquivo (sem \n) é ignorado."""
        fonte = "42#fim"
        assert remover_comentarios(fonte) == "42"

    # --- 5. LINHA VAZIA APÓS REMOVER COMENTÁRIO ---

    def test_linha_vazia_apos_comentario(self):
        """Linha que fica vazia após remover comentário não gera problema."""
        fonte = "# só comentário\n\n42"
        assert remover_comentarios(fonte) == "\n\n42"

    # --- 6. SEM COMENTÁRIO: IDENTIDADE ---

    def test_sem_comentario_nao_muda_nada(self):
        """Fonte sem # permanece inalterada."""
        fonte = "let x = 1 + 2 in x * 3"
        assert remover_comentarios(fonte) == fonte

    # --- 7. COMENTÁRIO APENAS O # ---

    def test_apenas_hash(self):
        """Uma linha com apenas # é removida."""
        fonte = "#\n42"
        assert remover_comentarios(fonte) == "\n42"
