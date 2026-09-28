# Design — Sistema de Avaliação de Filmes (RocketLab 2026.2)

## Contexto

A atividade (`stream.pdf`) pede um módulo Frontend (Vite + React + TS) e Backend (FastAPI + SQLite) de um sistema de avaliação de filmes estilo Letterboxd, usado pelo Administrador. O repositório base (`atividade-dev-rocket`) já traz FastAPI async, SQLAlchemy 2.0, Alembic e o esquema estrela (`app/movies/models.py`, migration `0001`), mas nenhum endpoint, carga de dados ou frontend. Os CSVs foram adicionados em `bases_atv_dev1/` e `bases_atv_dev_2/` (~222 MB, 95.645 filmes, 43.666 avaliações).

Requisitos obrigatórios: cadastrar filme (título, diretor, ano, gênero, sinopse); catálogo paginado; detalhes com avaliações; busca; editar/remover; nova avaliação (1–5 estrelas + resenha); média de avaliações por filme. README com passo a passo e versionamento no GitHub.

Decisões já tomadas com o usuário:
- **Escala**: estrelas de 1 a 5 em passos de 0,5 na UI; banco segue 0–10 (`nota = estrelas × 2`). Históricos exibidos convertidos (9.8 → 4,9★).
- **Dados**: CSVs compactados em `.csv.gz` em `backend/data/seed/`; seed lê gzip direto.
- **Extras**: autenticação admin JWT, filtros/ordenação, Storybook, E2E Playwright.
- **Comentários**: código novo sem comentários/docstrings; arquivos da base ficam como estão.
- **Commits**: mensagens em português (Conventional Commits, ex. `feat: adiciona caso de uso de cadastro de filme`), **sem** linha `Co-Authored-By` (instrução do usuário prevalece).
- Skills superpowers e code-review já estão instaladas — nada a instalar.

Dados como gabarito (orientação recebida em 2026-09-27): os CSVs são carregados sem tratamento. `dim_reviews.csv` é a média oficial; cada nova avaliação atualiza o resumo de forma incremental na mesma transação (`(média × qtd + nota) / (qtd + 1)`), sem recálculo a partir de `movie_reviews`.

## Arquitetura

### Backend — Clean Architecture por módulo (`backend/app/`)

```
app/
  core/            config (+ jwt_secret, admin_*), logging, security (base mantida)
  db/              base e session (base mantida)
  movies/
    models.py      ORM da base (mantido; é o adaptador de persistência)
    domain/        entities.py (Movie, MovieDetails, Review, RatingSummary), rating.py (VO Stars↔Score),
                   queries.py (MovieFilters, SortField, PageRequest, Page[T]), errors.py, ports.py (Protocols)
    application/   use_cases/ (create_movie, update_movie, delete_movie, get_movie_details,
                   list_movies, add_review, list_reviews, list_genres), commands.py (DTOs de entrada)
    infrastructure/ sqlalchemy_movie_repository.py, sqlalchemy_review_repository.py,
                   sqlalchemy_genre_repository.py, mappers.py, unit_of_work.py
    seed/          csv_reader.py (gzip; vazio → nulo), loader.py (bulk insert em lotes, sync engine)
  auth/
    domain/ (AdminUser, errors, ports: PasswordHasher, TokenService, AdminRepository)
    application/ (authenticate_admin, create_admin)
    infrastructure/ (models.py AdminUserModel, argon2 hasher via pwdlib, JWT via PyJWT, repo)
  api/v1/
    router.py      inclui routers (arquivo da base)
    dependencies.py  get_session, get_current_admin, fábricas de casos de uso
    movies/routes.py, movies/schemas.py; reviews/…; genres/…; auth/…
    error_handlers.py  domínio → HTTP (NotFound 404, Conflict 409, InvalidCredentials 401)
  cli.py           `python -m app.cli seed [--reset]` e `create-admin`
```
Regra de dependência: `domain` não importa nada de FastAPI/SQLAlchemy; `application` depende só de `domain` (ports); `infrastructure` e `api` dependem para dentro.

Migration nova `0002_admin_users` (tabela `admin_users`: id, email único, password_hash, nome, created_at). Seed cria o admin inicial a partir de `ADMIN_EMAIL`/`ADMIN_PASSWORD`/`ADMIN_NAME` do `.env`.

### API (`/api/v1`)
| Método | Rota | Auth |
|---|---|---|
| POST | `/auth/login` → `{access_token, token_type}` | – |
| GET | `/auth/me` | ✓ |
| GET | `/movies?page&page_size&q&genre_id&year_from&year_to&min_stars&sort=(titulo\|ano\|media\|popularidade)&order` → `Page` | – |
| POST | `/movies` (título, diretores[], data/ano, gêneros[], sinopse, duração, url_poster) → 201 | ✓ |
| GET | `/movies/{id}` → detalhes + gêneros, diretores, roteiristas, elenco, produtoras, desempenho, `media_estrelas`, `total_avaliacoes` | – |
| PUT | `/movies/{id}` | ✓ |
| DELETE | `/movies/{id}` → 204 (cascade) | ✓ |
| GET | `/movies/{id}/reviews?page&page_size` (mais recentes primeiro) | – |
| POST | `/movies/{id}/reviews` `{nome, estrelas, comentario}` → 201, atualiza `dim_reviews` | ✓ |
| GET | `/genres` | – |

Busca `q`: case-insensitive em título **ou** nome de diretor. Filme criado pelo admin recebe `id_filme` gerado (`adm-<hex>`); diretores via get-or-create em `dim_people` (tipo `Diretor`).

### Frontend (`frontend/`) — Vite + React + TS
Stack: React Router, TanStack Query (cache de consultas), react-hook-form + zod, Tailwind CSS, Vitest + Testing Library + MSW, Storybook, Playwright.
```
src/
  domain/          tipos (Movie, Review, Page), rating.ts (score↔estrelas, formatação)
  infrastructure/  http/client.ts (fetch + token + erros tipados), storage/token.ts
  features/
    auth/          api, AuthProvider, useAuth, LoginPage, RequireAuth
    movies/        api (hooks Query/Mutation), components (MovieCard, MovieGrid, SearchBar c/ debounce,
                   FiltersPanel, MovieForm, DeleteMovieDialog), pages (CatalogPage, MovieDetailsPage,
                   MovieCreatePage, MovieEditPage)
    reviews/       api, components (ReviewList, ReviewForm, RatingSummary)
  shared/ui/       Button, Input, TextArea, Select, StarRating (exibe frações; input em meias), Pagination,
                   Dialog, Toast, Skeleton, EmptyState  (+ *.stories.tsx)
  app/             router, providers, layout (header com busca e login/logout)
```
UI escura estilo Letterboxd, responsiva (mobile-first), estado da busca/filtros/página na URL (links compartilháveis), skeletons, estados vazio/erro, toasts. Ações de escrita visíveis só para admin logado.

### Dados / Seed
- `backend/data/seed/*.csv.gz` (gerados a partir das pastas `bases_*`, que saem do repositório e entram no `.gitignore`).
- Ordem: genres → companies → people → movies → bridges → performance → movie_reviews → dim_reviews, todos exatamente como no CSV. Lotes de ~5.000 linhas, uma transação, `PRAGMA` de performance durante a carga. Idempotente: pula se `dim_movies` já tem dados; `--reset` limpa antes.
- Apenas conversão de tipos: células vazias → `None`, datas ISO, floats/ints. Textos, durações `0` e nomes quase duplicados são preservados.

### DevOps
- `backend/Dockerfile` (python 3.12-slim + uv; entrypoint: `alembic upgrade head` → seed se vazio → uvicorn), `frontend/Dockerfile` (build Node → nginx servindo SPA + proxy `/api`), `docker-compose.yml` (volume para o SQLite, healthchecks).
- `.github/workflows/ci.yml`: backend (ruff check + format, mypy, pytest com cobertura), frontend (eslint, tsc, vitest, build, build-storybook), e2e (Playwright com banco de fixture), build das imagens Docker. `dependabot.yml`.
- `Makefile` (setup, dev, test, lint, seed, e2e, docker-up), `.pre-commit-config.yaml` (ruff, eslint/prettier), `.editorconfig`, `uv.lock`.

### Arquivos de projeto
- `CLAUDE.md` na raiz: stack, comandos, regras de arquitetura, TDD obrigatório, sem comentários no código novo, commits em PT sem coautoria, escala de notas.
- `README.md` reescrito: visão do produto, funcionalidades, arquitetura, passo a passo (local e Docker), testes, credenciais padrão, decisões (escala, `dim_reviews`).
- `docs/superpowers/specs/2026-09-24-sistema-avaliacao-filmes-design.md` (spec) e `docs/superpowers/plans/…` (plano detalhado por tarefa).

## Verificação

- `make test` → pytest (unit + integração + API) e vitest verdes; cobertura reportada.
- `make lint` → ruff, mypy, eslint, tsc sem erros.
- `make seed` num banco limpo: contagens batem com os CSVs (95.645 filmes, 43.666 avaliações) e `dim_reviews` com as 26.604 linhas do CSV.
- `docker compose up --build` → frontend em `http://localhost:8080`, API em `/api/v1`, `/docs` funcional.
- Validação manual no navegador (browser pane): login, busca, filtros, paginação, detalhes, avaliar (média atualiza), criar/editar/remover filme, layout mobile.
- `npx playwright test` cobrindo os fluxos acima; `npm run build-storybook` ok.
- Conferir que nenhum commit contém `Co-Authored-By` e que todas as mensagens estão em português (`git log`).
