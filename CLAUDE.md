# CLAUDE.md

Sistema de Avaliação de Filmes (RocketLab 2026.2): catálogo estilo Letterboxd operado por um Administrador.
Design completo em `docs/superpowers/specs/2026-09-24-sistema-avaliacao-filmes-design.md`.

## Stack

- Backend: FastAPI, SQLAlchemy 2.0 async (aiosqlite), Alembic, Pydantic v2, PyJWT, pwdlib (argon2). Python 3.12, gerenciado com `uv`.
- Frontend: Vite, React, TypeScript, React Router, TanStack Query, react-hook-form + zod, Tailwind CSS.
- Testes: pytest (+ pytest-asyncio, httpx), Vitest + Testing Library + MSW, Playwright, Storybook.
- Qualidade: ruff + mypy strict no backend; oxlint + tsc + Prettier no frontend.
- Banco: SQLite (`backend/rocketlab.db`). Dados iniciais em `backend/data/seed/*.csv.gz`.

## Comandos

```bash
make setup        # instala dependências do backend e do frontend
make migrate      # alembic upgrade head
make seed         # carrega os CSVs (idempotente); make seed-reset recarrega do zero
make dev          # backend :8000 e frontend :5173
make test         # pytest + vitest
make lint         # ruff, mypy, oxlint, tsc, prettier
make e2e          # Playwright (sobe API e web com banco e2e.db)
make storybook    # Storybook em :6006
docker compose up --build   # produto completo em http://localhost:8080
```

## Regras de desenvolvimento

- TDD obrigatório: teste falhando primeiro, implementação mínima, refatoração. Sem código de produção sem teste.
- Código novo sem comentários nem docstrings: nomes expressivos e funções pequenas. Arquivos herdados da base podem manter os seus.
- Clean Architecture por módulo (`app/movies`, `app/auth`):
  - `domain/` não importa FastAPI, SQLAlchemy nem Pydantic.
  - `application/` depende apenas de `domain` (ports como `Protocol`).
  - `infrastructure/` implementa os ports; `app/api/v1` só traduz HTTP ↔ casos de uso.
- Frontend: `domain/` puro, `infrastructure/` para HTTP/armazenamento, `features/<nome>` com api/components/pages, `shared/ui` sem regra de negócio. Todo componente de `shared/ui` tem story.
- Tabelas só mudam via migration Alembic.
- Commits pequenos, em português, no padrão Conventional Commits (`feat:`, `fix:`, `test:`, `refactor:`, `chore:`, `docs:`, `ci:`). Nunca adicionar `Co-Authored-By`.

## Domínio

- Notas são armazenadas de 0 a 10 (`movie_reviews.nota`). A interface usa estrelas de 1 a 5 em passos de 0,5: `nota = estrelas * 2`.
- `movie_reviews` é a fonte da verdade. `dim_reviews` é um resumo (quantidade e média) recalculado no seed e atualizado na mesma transação de cada nova avaliação.
- Leitura é pública; criar, editar, remover filmes e avaliar exige token JWT de administrador.
