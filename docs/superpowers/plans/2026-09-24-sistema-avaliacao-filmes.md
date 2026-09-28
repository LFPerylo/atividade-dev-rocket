# Sistema de Avaliação de Filmes — Plano de Implementação

> **Para agentes:** use superpowers:executing-plans (ou subagent-driven-development) tarefa a tarefa. Cada tarefa segue TDD: teste falhando → implementação mínima → testes verdes → refatoração → commit.

**Objetivo:** entregar o produto completo (API FastAPI + SPA React) que cumpre todos os requisitos da atividade, com autenticação, filtros, Storybook, E2E e DevOps.

**Arquitetura:** Clean Architecture por módulo no backend (domain → application → infrastructure/api) e por feature no frontend (domain → infrastructure → features → shared/ui).

**Stack:** Python 3.12, FastAPI, SQLAlchemy async, Alembic, PyJWT, pwdlib; Vite, React, TS, TanStack Query, Tailwind, Vitest, MSW, Storybook, Playwright; Docker, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-24-sistema-avaliacao-filmes-design.md`

## Restrições globais

- Código novo sem comentários/docstrings.
- Commits em português, Conventional Commits, sem `Co-Authored-By`.
- Nota persistida 0–10; entrada da API/UI em estrelas `{1.0, 1.5, …, 5.0}`; `nota = estrelas * 2`.
- Tabelas somente via Alembic; testes de integração rodam `alembic upgrade head` em SQLite temporário.
- `domain/` sem dependências de framework.

---

### Tarefa 1: Tooling do backend e fixture de banco
**Arquivos:** `backend/pyproject.toml`, `backend/uv.lock`, `backend/.python-version`, `backend/tests/conftest.py`, `.gitignore`, `.editorconfig`, `.pre-commit-config.yaml`, `backend/data/seed/*.csv.gz`
**Produz:** fixtures `database_url`, `session` (AsyncSession sobre banco migrado), `sync_engine`.
- [ ] Adicionar deps (`pyjwt`, `pwdlib[argon2]`, `email-validator`) e dev (`mypy`, `pytest-cov`); configurar mypy estrito para `domain`/`application`.
- [ ] Teste: `test_migrations_create_all_tables` (upgrade head em tmp → tabelas esperadas existem).
- [ ] `uv sync`, rodar suíte, commit `chore: configura tooling do backend e dados de carga compactados`.

### Tarefa 2: VO de avaliação (Stars/Score)
**Arquivos:** `app/movies/domain/rating.py`, `tests/unit/movies/test_rating.py`
**Produz:** `Stars.from_value(float) -> Stars` (valida 1..5, passo 0,5; `InvalidRating`), `Stars.to_score() -> float`, `score_to_stars(score: float) -> float` (arredonda 1 casa), `RatingSummary(count: int, average_score: float | None)` com `average_stars`.
- [ ] Testes: 4.5 → 9.0; 0.5, 5.5, 3.3 rejeitados; 9.8 → 4.9; resumo sem avaliações → `None`.

### Tarefa 3: Consultas, paginação, erros e entidades
**Arquivos:** `app/movies/domain/{queries,errors,entities,ports}.py`, testes unitários.
**Produz:** `PageRequest(page, size)` (page ≥ 1, 1 ≤ size ≤ 100, `offset`), `Page[T](items, total, page, size, pages)`, `SortField` (`TITULO`, `ANO`, `MEDIA`, `POPULARIDADE`), `SortOrder`, `MovieFilters(q, genre_id, year_from, year_to, min_stars)` (valida ano_from ≤ year_to), `MovieNotFound`, `GenreNotFound`, `InvalidMovieData`; entidades `MovieSummary`, `MovieDetails`, `Review`, `Person`, `Genre`, `Performance`; ports `MovieRepository`, `ReviewRepository`, `GenreRepository`, `PersonRepository`, `UnitOfWork`.
- [ ] Testes de validação de `PageRequest`, `Page.pages`, `MovieFilters`.

### Tarefa 4: Leitor e carga dos CSVs
**Arquivos:** `app/movies/seed/{csv_reader,loader}.py`, `tests/integration/seed/fixtures/*.csv.gz`, testes.
**Produz:** `read_rows(path) -> Iterator[dict]` normalizado; `SeedLoader(engine, data_dir).load(reset: bool) -> SeedReport`.
- [ ] Testes: vazio → `None`; sinopse `"…""x""…"` → `…"x"…`; duração 0 → `None`; carga de fixtures insere contagens corretas; `dim_reviews` = agregado de `movie_reviews`; segunda carga sem `reset` não duplica.

### Tarefa 5: Repositórios SQLAlchemy
**Arquivos:** `app/movies/infrastructure/*`, testes de integração.
- [ ] Listagem: paginação, busca por título e diretor (case-insensitive), filtros gênero/ano/estrelas mínimas, ordenações asc/desc.
- [ ] Detalhes com gêneros, pessoas por papel, produtoras, desempenho e resumo.
- [ ] Criar/atualizar (get-or-create de diretor, `id_filme` `adm-<hex>`), remover (cascade).
- [ ] Reviews: listar paginado (mais recentes primeiro), adicionar e recalcular `dim_reviews`.

### Tarefa 6: Casos de uso de filmes, avaliações e gêneros
**Arquivos:** `app/movies/application/*`, testes com fakes em memória.
- [ ] `ListMovies`, `GetMovieDetails` (404), `CreateMovie` (gênero inexistente → erro), `UpdateMovie`, `DeleteMovie`, `AddReview` (estrelas → nota), `ListReviews`, `ListGenres`.

### Tarefa 7: Autenticação
**Arquivos:** `migrations/versions/0002_admin_users.py`, `app/auth/**`, `app/cli.py`, testes.
- [ ] Hasher argon2, `JwtTokenService` (expiração, assinatura inválida), `AuthenticateAdmin` (credencial inválida → `InvalidCredentials`), `EnsureAdmin` (idempotente), CLI `seed` e `create-admin`.

### Tarefa 8: API HTTP
**Arquivos:** `app/api/v1/**`, `app/main.py`, testes de API.
- [ ] Rotas da spec, schemas Pydantic (entrada em estrelas, saída com `media_estrelas`), handlers de erro, dependência `get_current_admin` (401 sem token).

### Tarefa 9: Frontend — base
**Arquivos:** `frontend/**` (scaffold Vite), `src/domain`, `src/infrastructure/http`, `src/shared/ui` + stories, config Vitest/MSW/Tailwind/ESLint/Storybook.
- [ ] Testes: conversões de rating, cliente HTTP (token, erros tipados), `StarRating`, `Pagination`.

### Tarefa 10: Frontend — features
- [ ] Auth (login, logout, rota protegida), catálogo (busca com debounce, filtros, ordenação, paginação na URL), detalhes (informações, média, avaliações paginadas), formulário de avaliação, criar/editar/remover filme. Testes com Testing Library + MSW.

### Tarefa 11: DevOps
- [ ] Dockerfiles, `docker-compose.yml`, nginx, `Makefile`, `.github/workflows/ci.yml`, `dependabot.yml`.

### Tarefa 12: E2E, README e revisão
- [ ] Playwright (login, busca, detalhes, avaliar, CRUD), README completo, code review, verificação final.
