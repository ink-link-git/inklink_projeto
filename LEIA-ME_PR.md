# Pacote da branch `feat/integracao-cadastro`

**Ordem de merge:** 1º (base — faça o merge antes de todos)

## Como aplicar
1. `git checkout feat/integracao-cadastro` e `git merge main` (ou traga a base já mergeada).
2. Copie o conteúdo deste zip para a raiz do repositório, substituindo as pastas.
3. Apague o que ficou obsoleto: src/Cadastro_cliente (duplicada de login_cliente), arquivos soltos antigos de app/db na raiz de src, se existirem.
4. No Supabase rode: 04_liberar_rls_opcional.sql (opcional, só se o Supabase bloquear gravações).
5. `git add -A && git commit` com a mensagem abaixo, `git push` e abra o PR.

## Mensagem de commit sugerida
```
feat: base unificada (app factory, shared, logins e cadastro do tatuador)

- src/app.py registra só os módulos que existem na pasta src (cada branch roda sozinha)
- shared: sidebar do tatuador, decorators de login, tema.css (paleta/fontes do login)
- login_cliente, login_tatuador e Cadastro_tatuador integrados via sessão
- links para módulos ausentes viram "em breve"

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_016vLieaDErFvg8PQXVUe2wp
```

## Descrição do PR sugerida
**feat: base unificada (app factory, shared, logins e cadastro do tatuador)**

- src/app.py registra só os módulos que existem na pasta src (cada branch roda sozinha)
- shared: sidebar do tatuador, decorators de login, tema.css (paleta/fontes do login)
- login_cliente, login_tatuador e Cadastro_tatuador integrados via sessão
- links para módulos ausentes viram "em breve"

Roda sozinha: testada com a base + só este módulo; links para módulos ausentes aparecem como "em breve".

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_016vLieaDErFvg8PQXVUe2wp
